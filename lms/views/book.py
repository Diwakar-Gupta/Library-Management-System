import datetime

from django.http import Http404, HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.functional import cached_property
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator

from lms.models import (Account, Book, BookItem, BookLending, BookStatus,
                        LibraryConfig)
from lms.models.action import BookReservation

from rest_framework import generics, mixins, serializers, status
from rest_framework.response import Response

from .utils import AccountMixin


class BookMixin(AccountMixin, object):
    model = Book
    lookup_field = 'isbn'
    
    def get_object(self):
        if hasattr(self, 'queryset'):
            queryset = self.queryset
        else:
            queryset = self.get_queryset()         # Get the base queryset
        queryset = self.filter_queryset(queryset)  # Apply any filter backends

        filter = {
            self.lookup_field: self.kwargs[self.lookup_field]
        }
        book = get_object_or_404(queryset, **filter)  # Lookup the object
        if not book.is_accessible_by(self.request.user):
            raise Http404()
        return book


# Serializers define the API representation.
class UserBookSerializer(serializers.HyperlinkedModelSerializer):
    
    is_available = serializers.SerializerMethodField('is_available_bookitems')
    
    class Meta:
        model = Book
        fields = ['isbn', 'title', 'subject', 'publisher', 'language', 'numer_of_pages', 'is_available']
    
    def is_available_bookitems(self, book):
        return book.count_available_bookitems() > 0


class LibrarianBookSerializer(serializers.HyperlinkedModelSerializer):
    
    issued = serializers.SerializerMethodField('get_issued_bookitems')
    available = serializers.SerializerMethodField('get_available_bookitems')
    reserved = serializers.SerializerMethodField('get_reserved_bookitems')
    lost = serializers.SerializerMethodField('get_lost_bookitems')
    
    class Meta:
        model = Book
        fields = [
            'isbn', 'title', 'subject', 'publisher', 'language', 'numer_of_pages',
            'available',
            'reserved',
            'lost',
            'issued',
            ]
    
    def get_issued_bookitems(self, book):
        return book.count_issued_bookitems()
    
    def get_available_bookitems(self, book):
        return book.count_available_bookitems()
    
    def get_reserved_bookitems(self, book):
        return book.count_reserved_bookitems()
    
    def get_lost_bookitems(self, book):
        return book.count_lost_bookitems()


class BookListView(generics.ListAPIView):
    serializer_class = UserBookSerializer
    permission_classes = []
    filter_fields = (
        'isbn',
        'language',
        'publisher',
        'subject',
    )
    search_fields = [
        '$title',
    ]
    ordering_fields = [
        'numer_of_pages',
    ]

    def get_queryset(self):
        if Account.can_see_books(self.request.user):
            return Book.objects.all().order_by('title')
        else:
            raise Http404
    
    @method_decorator(cache_page(60 * 15), name='dispatch')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class BookDetail(
    BookMixin,
    mixins.RetrieveModelMixin,
    generics.GenericAPIView):
                
    queryset = Book.objects.all()

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)
    
    def get_serializer_class(self):
        if Account.is_librarian(self.request.user):
            return LibrarianBookSerializer
        return UserBookSerializer


class BookIssue(generics.GenericAPIView):

    permission_classes = []

    @cached_property
    def form(self):
        form_data = self.request.POST.dict()

        form_data['account'] = get_object_or_404(Account, id=form_data['account'])
        form_data['book_item'] = get_object_or_404(BookItem, barcode=form_data['book_item'])
        form_data['bypass_issue_quota'] = form_data['bypass_issue_quota'] in ['true', 'True']

        return form_data
    
    def form_valid(self, form):
        book_item = form['book_item']
        account = form['account']
        bypass_issue_quota = form['bypass_issue_quota']
            
        if hasattr(form, 'due_date'):
            due_date = datetime.datetime.strptime(form['due_date'], "%d%m%Y").date()
        else:
            max_day = LibraryConfig.object().maximum_day_limit
            due_date = datetime.datetime.now().date() + datetime.timedelta(days=max_day)

        if not account.is_active():
            return JsonResponse({'error':'Account not Active'}, status=400)

        if bypass_issue_quota == False and account.remaining_issue_count() <= 0:
            return JsonResponse({'error':'The user has already checked-out maximum number of books'}, status=400)

        if book_item.is_reserved():
            return JsonResponse({'error':'Book item is reserved'}, status=400)
        
        if not book_item.can_be_issued():
            return JsonResponse({'error':'Book item cannot be Issued'}, status=400)

        book_lend = BookLending.check_out(account, book_item, due_date)
        from lms.views.lending import BookLendingSerializer

        serializer = BookLendingSerializer(book_lend, many=False)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def post(self, request, *args, **kwargs):
        if not Account.can_checkout(request.user):
            return HttpResponseForbidden('Do you want me to ban you.')

        return self.form_valid(self.form)


class BookItemReservation(AccountMixin, generics.GenericAPIView):

    permission_classes = []

    @cached_property
    def form(self):
        form_data = self.request.POST.dict()

        form_data['account'] = get_object_or_404(Account, id=form_data['account'])
        form_data['book_item'] = get_object_or_404(BookItem, barcode=form_data['book_item'])

        return form_data
    
    def form_valid(self, form):
        book_item = form['book_item']
        account = form['account']

        can, mess = book_item.can_be_reserved()
        if not can:
            return JsonResponse({'error': mess}, status=status.HTTP_400_BAD_REQUEST)

        if account == self.account and not self.account.can_reserve_for_own():
            return HttpResponseForbidden("Can't reserve for own")
        
        if account != self.account and not Account.can_reserve_book_for_others(self.request.user):
            return HttpResponseForbidden("Can't reserve book")

        if book_item.is_reserved():
            return JsonResponse({'error':'Book item is reserved'}, status=400)

        book_reserve = BookReservation.reserve_book_item(account, book_item)
        from lms.views.reservation import BookReservationSerializer

        serializer = BookReservationSerializer(book_reserve, many=False)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def post(self, request, *args, **kwargs):
        if Account.can_reserve_book_for_others(request.user) or (self.account != None and self.account.can_reserve_for_own()):
            return self.form_valid(self.form)
        return HttpResponseForbidden('Do you want me to ban you.')


class BookItemSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField('get_title')
    format = serializers.CharField(source='get_format_display')
    status = serializers.CharField(source='get_status_display')
    
    class Meta:
        model = BookItem
        fields = ['barcode', 'title', 'format', 'is_reference_only', 'status', 'due_date', 'placed_at']
    
    def get_title(self, book_item):
        return book_item.get_title()


class BookItems(generics.ListAPIView):
    name = 'book-item-list'
    filter_fields = (
        'barcode',
        'format',
        'status',
        'is_reference_only',
        'book__isbn',
    )
    ordering_fields = [
        'due_date'
    ]

    def get_queryset(self):
        return BookItem.objects.all()
    
    def get_serializer_class(self):
        return BookItemSerializer

    @method_decorator(cache_page(60 * 15), name='dispatch')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


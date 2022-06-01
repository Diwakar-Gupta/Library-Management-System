import json
import datetime

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.db import transaction
from django.http import Http404, JsonResponse, HttpResponse, HttpResponseForbidden, HttpResponseRedirect
from django.utils.functional import cached_property
from django.shortcuts import get_object_or_404

from rest_framework import mixins, generics, serializers
from rest_framework.response import Response
from rest_framework import authentication

from lms.models import Book, BookItem, BookStatus, BookLending
from lms.models import Account
from lms.models import LibraryConfig


class BookMixin(object):
    model = Book
    lookup_field = 'isbn'
    
    @cached_property
    def account(self):
        if not self.request.user.is_authenticated:
            return None
        return self.request.user.account
    

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
        if not book.is_accessible_by(self.account):
            raise Http404()
        return book


# Serializers define the API representation.
class UserBookSerializer(serializers.HyperlinkedModelSerializer):
    
    is_available = serializers.SerializerMethodField('is_available_bookitems')
    
    class Meta:
        model = Book
        fields = ['isbn', 'title', 'subject', 'publisher', 'language', 'numer_of_pages', 'is_available']
    
    def is_available_bookitems(self, book):
        return BookItem.objects.filter(book=book, status=BookStatus.Available).exists()


class LibrarianBookSerializer(serializers.HyperlinkedModelSerializer):
    
    book_items = serializers.SerializerMethodField('get_total_bookitems')
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
            'book_items',
            ]
    
    def get_total_bookitems(self, book):
        return BookItem.objects.filter(book=book).count()
    
    def get_available_bookitems(self, book):
        return BookItem.objects.filter(book=book, status=BookStatus.Available).count()
    
    def get_reserved_bookitems(self, book):
        return BookItem.objects.filter(book=book, status=BookStatus.Reserved).count()
    
    def get_lost_bookitems(self, book):
        return BookItem.objects.filter(book=book, status=BookStatus.Lost).count()


class BookListView(generics.ListCreateAPIView):
    serializer_class = UserBookSerializer
    permission_classes = []

    def get_queryset(self):
        # TODO: filter for books that can be seen by this user
        return Book.objects.all()
    
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class BookDetail(
    BookMixin,
    mixins.RetrieveModelMixin,
    generics.GenericAPIView):
                
    queryset = Book.objects.all()

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)
    
    def get_serializer_class(self):
        if self.request.user.is_staff:
            return LibrarianBookSerializer
        return UserBookSerializer


class BookIssue(generics.GenericAPIView):

    permission_classes = []

    @cached_property
    def form(self):
        form_data = self.request.POST.dict()

        form_data['account'] = get_object_or_404(Account, id=form_data['account'])
        form_data['book_item'] = get_object_or_404(BookItem, barcode=form_data['book_item'])
        form_data['bypass_issue_quota'] in ['true', 'True']

        return form_data
    
    def form_valid(self, form):
        book_item = form['book_item']
        account = form['account']
        if form['due_date']:
            due_date = datetime.datetime.strptime(form['due_date'], "%d%m%Y").date()
        else:
            max_day = LibraryConfig.object().maximum_day_limit
            due_date = datetime.datetime.now().date() + datetime.timedelta(days=max_day)
            
        bypass_issue_quota = form['bypass_issue_quota']

        if not account.is_active():
            return JsonResponse({'error':'Account not Active'}, status=400)

        if bypass_issue_quota == False and account.remaining_issue_count() <= 0:
            return JsonResponse({'error':'Max BookIssue limit exceed'}, status=400)

        if book_item.is_reserved():
            return JsonResponse({'error':'Book item is reserved'}, status=400)
        
        if not book_item.can_be_issued():
            return JsonResponse({'error':'Book item cannot be Issued'}, status=400)

        book_lend = BookLending.check_out(account, book_item, due_date)
        from lms.views.lending import BookLendingSerializer

        serializer = BookLendingSerializer(book_lend, many=False)
        return Response(serializer.data)        

    def post(self, request, *args, **kwargs):
        if not Account.can_checkout(request.user):
            return HttpResponseForbidden('Do you want me to ban you.')

        return self.form_valid(self.form)


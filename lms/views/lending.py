import datetime

from django.core.exceptions import PermissionDenied
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, resolve_url
from django.utils.decorators import method_decorator
from django.utils.functional import cached_property
from django.views.decorators.cache import cache_page
from django.views.decorators.cache import cache_control

from lms.models import Account, BookItem, BookLending
from lms.views.utils import AccountMixin

from rest_framework import generics, mixins, serializers, status
from rest_framework.response import Response


class LendingPermissionDenied(PermissionDenied):
    def __init__(self, lend):
        self.lend = lend


class AccountSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField('get_name')
    
    class Meta:
        model = Account
        fields = ['id', 'name', 'status', 'issued_book_count']
    
    def get_name(self, account):
        return account.get_name()


class BookItemSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField('get_title')
    format = serializers.CharField(source='get_format_display')
    
    class Meta:
        model = BookItem
        fields = ['barcode', 'title', 'format']
    
    def get_title(self, book_item):
        return book_item.get_title()


class BookLendingSerializer(serializers.ModelSerializer):
    account = AccountSerializer(many=False)
    book_item = BookItemSerializer(many=False)
    fine =  serializers.SerializerMethodField('get_fine')

    class Meta:
        model = BookLending
        fields = ['pk', 'account', 'book_item', 'creation_date', 'due_date', 'return_date', 'fine']

    def get_fine(self, lending):
        if not lending.return_date:
            return -1
        if hasattr(lending, 'fine'):
            return lending.fine.amount
        else:
            return 0


class LendingListBase(AccountMixin, generics.ListAPIView):

    def get_queryset(self):
        # all lending that logged in user can see
        if Account.can_see_all_lendings(self.request.user):
            queryset = BookLending.objects.all()
        else:
            queryset = BookLending.objects.filter(account=self.account)
            
        return queryset


class AllLendings(LendingListBase):
    
    filter_fields = (
        'account__id',
        'book_item__barcode',
    )
    ordering_fields = [
        'creation_date',
        'due_date',
        'return_date',
    ]

    def get_serializer_class(self):
        return BookLendingSerializer
    
    # Should be removed if student & librarian has different serializer
    @method_decorator(cache_page(60 * 15), name='dispatch')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class AllUserLendings(LendingListBase):
    lookup_field = 'id'

    filter_fields = (
        'account__id',
        'book_item__barcode',
    )
    ordering_fields = [
        'creation_date',
        'due_date',
        'return_date',
    ]

    @cached_property
    def query_account(self):
        account = get_object_or_404(Account, id=self.kwargs[self.lookup_field])
        return account

    @cached_property
    def is_own(self):
        return self.account == self.query_account

    def get_queryset(self):
        if not Account.can_see_all_lendings(self.request.user) and not self.is_own:
            raise PermissionDenied()
        queryset = super(AllUserLendings, self).get_queryset()
        queryset = queryset.filter(account = self.query_account)
        return queryset
    
    def get_serializer_class(self):
        return BookLendingSerializer

    # @method_decorator(cache_control(max_age=60*15, private=True), name='dispatch')
    def get(self, request, *args, **kwargs):
        if self.lookup_field not in kwargs:
            if self.account == None:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            return redirect(resolve_url('user_lendings_list', id=self.account.id))
        return super(AllUserLendings, self).get(request, *args, **kwargs)


class LendingReturnMixin():

    def form(self):
        form_data = self.request.POST.dict()

        return form_data
    
    def form_valid(self, form):
        return_info={}
        return_date = datetime.datetime.now().date()

        is_correct, message =  self.lending.validate_return_data(return_info)

        if not is_correct:
            return JsonResponse({'error': message}, status=400)

        self.lending.return_book_item(return_date)

        serializer = self.serializer_class(self.lending, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        if not Account.can_return(request.user):
            return HttpResponseForbidden('Do you want me to ban you.')

        return self.form_valid(self.form())


class LendingDetail(AccountMixin, LendingReturnMixin, mixins.RetrieveModelMixin, generics.GenericAPIView):

    lookup_fields = ['pk', 'barcode']
    serializer_class = BookLendingSerializer

    @cached_property
    def lending(self):
        return self.get_object()

    def get_object(self):
        if 'pk' in self.kwargs:
            lending = get_object_or_404(BookLending, pk=self.kwargs['pk'])
        elif 'barcode' in self.kwargs:
            lending = get_object_or_404(BookLending, return_date=None, book_item__barcode = self.kwargs['barcode'])
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if Account.can_see_lending(self.request.user, lending):
            return lending
        else:
            raise PermissionDenied()

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


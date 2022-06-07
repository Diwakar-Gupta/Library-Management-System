import datetime

from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect
from django.utils.functional import cached_property

from lms.models import BookLending
from lms.models import Account
from lms.models import BookItem

from rest_framework import generics, mixins, serializers
from rest_framework.response import Response
from rest_framework import status

from lms.views.utils import AccountMixin


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
    
    def get(self, request, *args, **kwargs):
        if self.lookup_field not in kwargs:
            if self.account == None:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            return redirect('/lendings/user/{}/'.format(self.account.id))
        return super(AllUserLendings, self).get(request, *args, **kwargs)


class LendingBarcode(AccountMixin, mixins.RetrieveModelMixin, generics.GenericAPIView):

    lookup_field = 'barcode'
    serializer_class = BookLendingSerializer

    @cached_property
    def lending(self):
        lending = get_object_or_404(BookLending, return_date=None, book_item__barcode = self.kwargs[self.lookup_field])
        if Account.can_see_all_lendings(self.request.user):
            return lending
        elif self.account != None and self.account.can_see_lending(lending):
            return lending
        else:
            raise PermissionDenied()

    def get_object(self):
        return self.lending

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def form(self):
        form_data = self.request.POST.dict()

        return form_data
    
    def form_valid(self, form):
        return_date = datetime.datetime.now().date()
        self.lending.return_book_item(return_date)

        serializer = self.serializer_class(self.lending, many=False)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        if not Account.can_return(request.user):
            return HttpResponseForbidden('Do you want me to ban you.')

        return self.form_valid(self.form())


class LendingDetail(AccountMixin, mixins.RetrieveModelMixin, generics.GenericAPIView):

    lookup_field = 'pk'
    serializer_class = BookLendingSerializer

    def get_object(self):
        lending = get_object_or_404(BookLending, pk=self.kwargs['pk'])
        if lending.account == self.account:
            return lending
        elif self.account.can_see_lending(lending):
            return lending
        else:
            raise PermissionDenied()

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


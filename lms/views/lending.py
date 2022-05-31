from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.utils.functional import cached_property

from lms.models import BookLending
from lms.models.account import Account
from lms.models.book import BookItem

from rest_framework import generics, mixins, serializers


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
    
    class Meta:
        model = BookItem
        fields = ['barcode', 'title', 'format']
    
    def get_title(self, book_item):
        return book_item.get_title()


class BookLendingSerializer(serializers.ModelSerializer):
    account = AccountSerializer(many=False)
    book_item = BookItemSerializer(many=False)

    class Meta:
        model = BookLending
        fields = ['account', 'book_item', 'creation_date', 'due_date']


class LendingListBase(generics.ListAPIView):
    
    @cached_property
    def account(self):
        return self.request.user.account

    def get_queryset(self):
        # all lending that logged in user can see
        if Account.can_see_lendings(self.request.user):
            queryset = BookLending.objects.all()
        else:
            queryset = BookLending.objects.filter(account=self.account)
            
        return queryset


class AllLendings(LendingListBase):
    
    def get_serializer_class(self):
        return BookLendingSerializer


class AllUserLendings(LendingListBase):
    lookup_field = 'id'

    @cached_property
    def query_account(self):
        account = get_object_or_404(Account, id=self.kwargs[self.lookup_field])
        return account

    def get_queryset(self):
        queryset = super(AllUserLendings, self).get_queryset()
        queryset = queryset.filter(account = self.query_account)
        return queryset
    
    def get_serializer_class(self):
        return BookLendingSerializer


class LendingDetail(mixins.RetrieveModelMixin,
                    mixins.UpdateModelMixin,
                    generics.GenericAPIView):

    lookup_field = 'barcode'
    serializer_class = BookLendingSerializer

    @cached_property
    def account(self):
        return self.request.user.account

    def get_object(self):
        lending = get_object_or_404(BookLending, account=self.account, book_item__barcode = self.kwargs[self.lookup_field])
        return lending
    
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    # def post(self, request, *args, **kwargs):
    #     pass

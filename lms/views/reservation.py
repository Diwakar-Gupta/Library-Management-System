from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect
from django.utils.decorators import method_decorator
from django.utils.functional import cached_property
from django.views.decorators.cache import cache_page
from django.views.decorators.cache import cache_control

from lms.models import Account, BookReservation
from lms.models.action import ReservationStatus
from lms.models.book import BookItem
from lms.views.utils import AccountMixin

from rest_framework import generics, mixins, serializers, status
from rest_framework.response import Response


class AccountSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField('get_name')
    status = serializers.CharField(source='get_status_display')
    
    class Meta:
        model = Account
        fields = ['id', 'name', 'status']
    
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


class BookReservationSerializer(serializers.ModelSerializer):
    account = AccountSerializer(many=False)
    book_item = BookItemSerializer(many=False)
    status = serializers.CharField(source='get_status_display')

    class Meta:
        model = BookReservation
        fields = ['pk', 'account', 'book_item', 'creation_date', 'status']


class ReservationListBase(AccountMixin, generics.ListAPIView):

    def get_queryset(self):
        # all lending that logged in user can see
        if Account.can_see_all_reservations(self.request.user):
            queryset = BookReservation.objects.all()
        else:
            queryset = BookReservation.objects.filter(account=self.account)
            
        return queryset


class AllReservations(ReservationListBase):
    
    filter_fields = (
        'book_item__barcode',
        'account__id',
        'status',
    )
    ordering_fields = [
        'creation_date',
    ]

    def get_serializer_class(self):
        return BookReservationSerializer
    
    # Should be removed if student & librarian has different serializer
    @method_decorator(cache_page(60 * 15), name='dispatch')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class AllUserReservations(ReservationListBase):
    lookup_field = 'id'

    @cached_property
    def query_account(self):
        account = get_object_or_404(Account, id=self.kwargs[self.lookup_field])
        return account

    def get_queryset(self):
        queryset = super(AllUserReservations, self).get_queryset()
        queryset = queryset.filter(account = self.query_account)
        return queryset
    
    def get_serializer_class(self):
        return BookReservationSerializer
    
    @method_decorator(cache_control(private=True), name='dispatch')
    def get(self, request, *args, **kwargs):
        if self.lookup_field not in kwargs:
            if self.account == None:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            return redirect('/reservations/user/{}/'.format(self.account.id))
        return super(AllUserReservations, self).get(request, *args, **kwargs)


class ReservationDetail(AccountMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, generics.GenericAPIView):

    lookup_fields = ['pk', 'barcode']
    serializer_class = BookReservationSerializer

    def get_object(self):
        if 'pk' in self.kwargs:
            reservation = get_object_or_404(BookReservation, pk=self.kwargs['pk'])
        elif 'barcode' in self.kwargs:
            reservation = get_object_or_404(BookReservation, book_item__barcode=self.kwargs['barcode'], status=ReservationStatus.Waiting)
        if reservation.account == self.account:
            return reservation
        elif self.account.can_see_reservation(reservation):
            return reservation
        else:
            raise PermissionDenied()

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        
        reservation = self.get_object()
        if reservation.is_editable_by(request.user):
            if 'status' in request.data and request.data['status'].lower() == 'canceled':
                obj = reservation.cancel_reservation()

                # serializer = self.serializer_class(obj, many=False)
                return Response(status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)


from django.conf import settings
from django.http import JsonResponse
from django.urls import include, path

from lms.views import book, lending, reservation

urlpatterns = [
    path('books/', book.BookListView.as_view(), name='book_list'),
    path('book/<str:isbn>/', include([
        path('', book.BookDetail.as_view(), name='book_detail'),
    ])),

    path('book-item/', include([
        path('', book.BookItems.as_view(), name='book_item_list'),
        path('issue/', book.BookIssue.as_view(), name='book_issue'),
        path('reserve/', book.BookItemReservation.as_view(), name='book_reservation')
    ])),
    
    path('lendings/', include([
        path('', lending.AllLendings.as_view(), name='lendings_list'),
        path('<int:pk>/', lending.LendingDetail.as_view(), name='lendings_detail'),
        path('barcode/<str:barcode>/', lending.LendingDetail.as_view(), name='lendings_return'),
        path('user/', lending.AllUserLendings.as_view(), name='my_lendings_list'),
        path('user/<int:id>/', lending.AllUserLendings.as_view(), name='user_lendings_list'),
    ])),

    path('reservations/', include([
        path('', reservation.AllReservations.as_view(), name='reservations_list'),
        path('<int:pk>/', reservation.ReservationDetail.as_view(), name='reservations_detail'),
        path('barcode/<str:barcode>/', reservation.ReservationDetail.as_view(), name='reservations_detail_barcode'),
        path('user/', reservation.AllUserReservations.as_view(), name='my_reservations_list'),
        path('user/<int:id>/', reservation.AllUserReservations.as_view(), name='user_reservations_list'),
    ])),
]


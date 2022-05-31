from django.urls import path, include
from lms.views import book, lending


from . import views

urlpatterns = [
    path('books/', book.BookListView.as_view(), name='book_list'),
    path('book/<str:isbn>/', include([
        path('', book.BookDetail.as_view(), name='book_detail'),
        path('issue/', book.BookIssue.as_view(), name='book_issue'),
    ])),
    
    path('lendings/', include([
        path('', lending.AllLendings.as_view(), name='lendings_list'),
        path('user/<int:id>', lending.AllUserLendings.as_view(), name='user_lendings_list'),
        path('<str:barcode>/', lending.LendingDetail.as_view(), name='lendings_detail'),
        
        # path('return/', lending.???.as_view(), name='issue_book'),
    ])),
]
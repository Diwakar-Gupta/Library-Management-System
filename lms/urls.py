from django.urls import path
from lms.views import book

from . import views

urlpatterns = [
    path('', book.BookListView.as_view(), name='book-list'),
]
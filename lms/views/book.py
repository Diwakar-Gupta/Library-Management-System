from django.views.generic import ListView
from rest_framework.generics import ListAPIView
from lms.models import Book, BookItem
from rest_framework import serializers


# Serializers define the API representation.
class BookSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Book
        fields = ['ISBN', 'title', 'subject', 'publisher', 'language', 'numer_of_pages']


class BookListView(ListAPIView):
    serializer_class = BookSerializer


    def get_queryset(self):
        return Book.objects.all()


import datetime

from django.core.exceptions import PermissionDenied
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, resolve_url
from django.utils.cache import patch_vary_headers
from django.utils.decorators import method_decorator
from django.utils.functional import cached_property
from django.views.decorators.cache import cache_control, cache_page
from django.views.decorators.vary import vary_on_headers

from lms.models import Notification
from lms.views.utils import AccountMixin

from rest_framework import generics, serializers, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class NotificationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Notification
        fields = ['pk', 'created_on', 'content', 'is_read']


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 50


class AllNotification(AccountMixin, generics.ListAPIView):
    
    filter_fields = (
        'is_read',
    )
    ordering_fields = [
        'created_on',
    ]
    pagination_class = StandardResultsSetPagination

    serializer_class = NotificationSerializer
    
    def get_queryset(self):
        notifications = Notification.objects.filter(account=self.account)
        return notifications

    @method_decorator(cache_control(max_age=60*5, private=True), name='dispatch')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class NotificationDetail(AccountMixin, generics.ListAPIView):
    lookup_field = 'pk'
    serializer_class = NotificationSerializer

    def get_object(self):
        notification = get_object_or_404(Notification, account=self.account, pk=self.kwargs.pk)
        return notification

    def post(self, request, *args, **kwargs):
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response(status=status.HTTP_200_OK)


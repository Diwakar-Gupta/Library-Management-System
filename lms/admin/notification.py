from django.contrib import admin


class NotificationAdmin(admin.ModelAdmin):
    readonly_fields=('account', 'created_on', 'content', 'is_read')
    list_display = ['account', 'created_on']
    list_filter = ("is_read", 'created_on')


from django.contrib import admin


class AccountAdmin(admin.ModelAdmin):
    readonly_fields = ['issued_book_count']
    list_display = ['id', 'name', 'status',]
    list_filter = ("status", )
    actions_on_top = True
    actions = ['recalculate_issued_count']

    def name(self, account):
        return account.get_name()

    @admin.action(permissions=['change'])
    def recalculate_issued_count(modeladmin, request, queryset):
        pass
from django.contrib import admin


def recalculate_issued_count(self, request, queryset):
    pass

class AccountAdmin(admin.ModelAdmin):
    readonly_fields = ['issued_book_count']
    actions = ('recalculate_issued_count',)
    list_display = ['id', 'name', 'status']
    list_filter = ("status", )
    actions_on_top = True

    def name(self, account):
        return account.get_name()

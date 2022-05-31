from django.contrib import admin


def recalculate_issued_count(self, request, queryset):
    pass

class AccountAdmin(admin.ModelAdmin):
    readonly_fields = ['issued_book_count']
    actions = ('recalculate_issued_count')
    actions_on_top = True
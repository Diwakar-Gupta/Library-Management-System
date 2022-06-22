from django.contrib import admin


class BookItemAdmin(admin.ModelAdmin):
    readonly_fields=('borrowed', 'due_date', 'status')
    actions = ('recalculate_score')
    list_display = ['barcode', 'status', 'due_date']
    list_filter = ("status", )
    ordering = ['due_date']


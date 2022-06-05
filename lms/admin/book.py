from django.contrib import admin


class BookItemAdmin(admin.ModelAdmin):
    readonly_fields=('borrowed', 'due_date', 'status')
    actions = ('recalculate_score')
    list_display = ['barcode', 'status']
    list_filter = ("status", )


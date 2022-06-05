from django.contrib import admin


class BookLendingAdmin(admin.ModelAdmin):
    readonly_fields=('creation_date', 'due_date', 'return_date')
    list_display = ['barcode', 'return_date']

    def barcode(self, lending):
        return str(lending)


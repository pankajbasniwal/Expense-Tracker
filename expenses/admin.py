from django.contrib import admin
from .models import Category, Transaction, Budget


# Register Category Model
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'name', 'category_type')
    search_fields = ('name',)
    list_filter = ('category_type',)


# Register Transaction Model
@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'category',
        'transaction_type',
        'amount',
        'date'
    )

    search_fields = ('description',)
    list_filter = ('transaction_type', 'date')


# Register Budget Model
@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'category', 'amount', 'month')
    list_filter = ('month',)
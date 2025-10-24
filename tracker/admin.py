from django.contrib import admin
from .models import Category, Transaction, RecurringTransaction, CreditCard

admin.site.register(Category)
admin.site.register(Transaction)
admin.site.register(RecurringTransaction)
admin.site.register(CreditCard)
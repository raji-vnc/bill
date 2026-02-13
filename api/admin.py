from django.contrib import admin

from .models import Product, Bill, BillItem,BillingSetting
admin.site.register(Product)
admin.site.register(Bill)
admin.site.register(BillItem)
admin.site.register(BillingSetting)
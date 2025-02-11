from django.contrib import admin
from .models import *


class ProductSizeInline(admin.TabularInline):
    model = ProductSize
    extra = 1


class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductSizeInline]


admin.site.register(UserProfile)
admin.site.register(Seller)
admin.site.register(Group)
admin.site.register(Product, ProductAdmin)
admin.site.register(History)
admin.site.register(HistoryItem)

from django.contrib import admin
from .models import Category, Product
from django.utils.html import format_html
#from orders.models import Order
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ('name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock', 'is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    def stock_status(self, obj):
        if obj.stock > 10:
            return format_html('<span class="badge badge-success">En stock</span>')
        elif obj.stock > 0:
            return format_html('<span class="badge" style="background:#fff3cd;color:#856404;">Faible</span>')
        else:
            return format_html('<span class="badge badge-danger">Rupture</span>')

    stock_status.short_description = "Stock"
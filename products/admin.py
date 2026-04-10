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

    def status_badge(self, obj):
        if obj.is_active:
            return format_html('<span class="badge badge-success">Actif</span>')
        return format_html('<span class="badge badge-danger">Inactif</span>')

    status_badge.short_description = "Statut"
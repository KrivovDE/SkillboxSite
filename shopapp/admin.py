from django.contrib import admin

from shopapp.models import Product, Order


class OrderInline(admin.TabularInline):
    model = Product.orders.through

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [OrderInline]
    list_display = 'pk', 'name', 'description_short', 'price', 'discount'
    list_display_links = 'pk', 'name'
    ordering = 'pk',
    search_fields = 'name', 'description'
    fieldsets = [
        (None, {
            'fields': ('name', 'description'),
        }),
        ('Price options', {
            'fields': ('price', 'discount'),
            'classes': ('wide', 'collapse'),
        }),
        ('Extra options', {
            'fields': ('archived',),
            'classes': ('wide', 'collapse'),
            'description': "Extra options. Field 'archived' is for soft delete",
        })
    ]

    def description_short(self, obj: Product) -> str:
        if len(obj.description) < 48:
            return obj.description
        return f'{obj.description[:48]}...'


# admin.site.register(Product, ProductAdmin) -- так нужно сделать если не используешь декоратор

class ProductInline(admin.TabularInline):
    model = Order.products.through


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [ProductInline]
    list_display = 'delivery_address', 'promocode', 'created_at', 'user_verbose'

    def get_queryset(self, request):
        return Order.objects.select_related('user').prefetch_related('products')

    def user_verbose(self, obj: Order) -> str:
        return obj.user.first_name or obj.user.username

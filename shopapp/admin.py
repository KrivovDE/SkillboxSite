from django.contrib import admin

from shopapp.models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = 'pk', 'name', 'description_short', 'price', 'discount'
    list_display_links = 'pk', 'name'

    def description_short(self, obj: Product) -> str:
        if len(obj.description) < 48:
            return obj.description
        return f'{obj.description[:48]}...'


# admin.site.register(Product, ProductAdmin) -- так нужно сделать если не используешь декоратор на 6стр
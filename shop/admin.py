from django.contrib import admin

from shop.models import (
    Product, PurchaseOrder, OrderDetails, PgNotify, PgReturn)


class ProductAdmin(admin.ModelAdmin):
    model = Product
    list_display = (
        "code", "name", "price", "days", "reward", "is_active", "c_on",
        "course", "chapter")


class PgReturnAdmin(admin.ModelAdmin):
    model = PgReturn
    list_display = ("order_id", "token", "c_on", "response")


class PgNotifyAdmin(admin.ModelAdmin):
    model = PgNotify
    list_display = ("order_id", "pg_name", "c_on", "response")


admin.site.register(Product, ProductAdmin)
admin.site.register(PurchaseOrder)
admin.site.register(OrderDetails)
admin.site.register(PgNotify, PgNotifyAdmin)
admin.site.register(PgReturn, PgReturnAdmin)

from django.contrib import admin
from .models import Product, Order, RefundRequest


class ProductAdmin(admin.ModelAdmin):
    list_display = ["name", "category", "price", "in_stock"]
    list_filter = ["category", "in_stock"]
    search_fields = ["name", "description"]
    ordering = ["name"]


class OrderAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "user",
        "product",
        "amount",
        "status",
        "carrier",
        "tracking_number",
        "created_at",
        "updated_at",
    ]
    list_filter = ["status", "carrier"]
    search_fields = ["user__username", "product_name", "tracking_number"]
    list_editable = ["status", "carrier", "tracking_number"]
    readonly_fields = ["created_at", "updated_at"]
    date_hierarchy = "created_at"
    ordering = ["-created_at"]
    raw_id_fields = ["user", "product"]
    fieldsets = (
        (None, {
            "fields": (
                "user",
                "product",
                "product_name",
                "amount",
                "status",
            )
        }),
        ("Shipping", {
            "fields": ("carrier", "tracking_number", "delivery")
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at")
        }),
    )


class RefundRequestAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "order", "status", "created_at"]
    list_filter = ["status"]
    search_fields = ["user__username", "order__product_name", "reason"]
    readonly_fields = ["created_at"]
    date_hierarchy = "created_at"
    ordering = ["-created_at"]
    raw_id_fields = ["user", "order"]


admin.site.register(Product, ProductAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(RefundRequest, RefundRequestAdmin)

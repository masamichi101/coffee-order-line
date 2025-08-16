from django.contrib import admin
from app.models import Shop, Product, Cart, CartItem, Order, OrderItem, Customer


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ["name", "user", "is_active", "open_time", "close_time", "created_at"]
    list_filter = ["is_active", "created_at"]
    search_fields = ["name", "user__name", "address"]
    ordering = ["-created_at"]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["name", "shop", "category", "price", "is_available", "stock", "created_at"]
    list_filter = ["category", "is_available", "shop", "created_at"]
    search_fields = ["name", "shop__name", "description"]
    ordering = ["shop", "category", "name"]


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ["customer", "item_count", "total_price", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["customer__name", "customer__line_id"]
    ordering = ["-created_at"]


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ["cart", "product", "quantity", "subtotal", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["cart__customer__name", "product__name"]
    ordering = ["-created_at"]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["id", "customer", "shop", "status", "total_amount", "created_at"]
    list_filter = ["status", "shop", "created_at"]
    search_fields = ["customer__name", "shop__name", "note"]
    ordering = ["-created_at"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ["order", "product", "quantity", "price", "subtotal", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["order__customer__name", "product__name"]
    ordering = ["-created_at"]


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ["name", "gender", "phone_number", "line_id", "created_at"]
    list_filter = ["gender", "created_at"]
    search_fields = ["name", "line_id", "phone_number"]
    ordering = ["-created_at"]
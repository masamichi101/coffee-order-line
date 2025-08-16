from django import forms
from app.models import Shop, Product, CartItem, Order


class ShopRegisterForm(forms.ModelForm):
    class Meta:
        model = Shop
        fields = [
            "name",
            "address",
            "tel",
            "description",
            "image",
            "logo",
            "open_time",
            "close_time",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"}),
            "address": forms.TextInput(attrs={"class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"}),
            "tel": forms.TextInput(attrs={"class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"}),
            "description": forms.Textarea(attrs={"class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500", "rows": 4}),
            "image": forms.FileInput(attrs={"class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"}),
            "logo": forms.FileInput(attrs={"class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"}),
            "open_time": forms.TimeInput(attrs={"type": "time", "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"}),
            "close_time": forms.TimeInput(attrs={"type": "time", "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"}),
        }


class ProductRegisterForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["shop", "name", "category", "description", "price", "image", "stock"]
        widgets = {
            "shop": forms.Select(attrs={"class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"}),
            "name": forms.TextInput(attrs={"class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"}),
            "category": forms.Select(attrs={"class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"}),
            "description": forms.Textarea(attrs={"class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500", "rows": 4}),
            "price": forms.NumberInput(attrs={"class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500", "min": 0}),
            "image": forms.FileInput(attrs={"class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"}),
            "stock": forms.NumberInput(attrs={"class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500", "min": 0}),
        }


class CartItemForm(forms.ModelForm):
    class Meta:
        model = CartItem
        fields = ["quantity"]
        widgets = {
            "quantity": forms.NumberInput(attrs={"min": "1", "max": "99", "class": "w-16 px-2 py-1 border rounded text-center"}),
        }


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["note"]
        widgets = {
            "note": forms.Textarea(attrs={"class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500", "rows": 3, "placeholder": "注文に関する備考があれば入力してください"}),
        }

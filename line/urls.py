from django.urls import path
from . import views

app_name = "line"

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("product/<int:shop_id>/", views.ProductView.as_view(), name="product"),
    path("cart/", views.CartView.as_view(), name="cart"),
    path("order/confirm/", views.OrderConfirmView.as_view(), name="order_confirm"),
    path("order/complete/<int:order_id>/", views.OrderCompleteView.as_view(), name="order_complete"),
    path("order/history/", views.OrderHistoryView.as_view(), name="order_history"),
    path("order/cancel/<int:order_id>/", views.OrderCancelView.as_view(), name="order_cancel"),
    path("line-required/", views.LineRequiredView.as_view(), name="line_required"),
    path("callback/", views.CallbackView.as_view(), name="callback"),
]

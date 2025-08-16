from django.urls import path, include
from . import views

app_name = "app"

urlpatterns = [
    # 管理者用（ログイン必須）- ホームページ
    path("", views.ShopManageView.as_view(), name="shop_manage"),
    
    
    # 顧客向け（LINE認証必須）
    path("customer/", views.IndexView.as_view(), name="index"),
    path("shop/<int:shop_id>/", views.ShopDetailView.as_view(), name="shop_detail"),
    path("cart/", views.CartView.as_view(), name="cart"),
    path("order/confirm/", views.OrderConfirmView.as_view(), name="order_confirm"),
    path("order/complete/<int:order_id>/", views.OrderCompleteView.as_view(), name="order_complete"),
    path("order/history/", views.OrderHistoryView.as_view(), name="order_history"),
    path("order/cancel/<int:order_id>/", views.OrderCancelView.as_view(), name="order_cancel"),
    
    # LINE認証が必要なページ（lineアプリに移動）
    path("line-", include("line.urls")),
    
    # 管理者用（ログイン必須）
    path("shop/register/", views.ShopRegisterView.as_view(), name="shop_register"),
    path("shop/edit/<int:shop_id>/", views.ShopEditView.as_view(), name="shop_edit"),
    path("product/register/", views.ProductRegisterView.as_view(), name="product_register"),
    path("product/edit/<int:product_id>/", views.ProductEditView.as_view(), name="product_edit"),
    path("product/manage/<int:shop_id>/", views.ProductManageView.as_view(), name="product_manage"),
    path("order/manage/", views.OrderManageView.as_view(), name="order_manage"),
    path("order/detail/<int:order_id>/", views.OrderDetailView.as_view(), name="order_detail"),
]

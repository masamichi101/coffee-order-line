from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Q
from .models import Shop, Product, Cart, CartItem, Order, OrderItem, Customer
from .forms import ShopRegisterForm, ProductRegisterForm, CartItemForm, OrderForm
from django.urls import reverse

# ヘルパー関数: line_id付きのURLを構築
def build_url_with_line_id(view_name, line_id=None, **kwargs):
    """
    line_id付きのURLを構築するヘルパー関数
    
    Args:
        view_name: URL名（例: 'app:cart'）
        line_id: LINE ID（オプション）
        **kwargs: URLパラメータ（例: shop_id=1）
    
    Returns:
        構築されたURL
    """
    url = reverse(view_name, kwargs=kwargs)
    if line_id:
        url += f"?line_id={line_id}"
    return url


# LINEユーザーのみアクセス可能にするミックスイン
class LineUserRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        line_id = request.GET.get("line_id")
        if not line_id:
            messages.error(request, "LINE IDが必要です。LINEアプリからアクセスしてください。")
            return redirect("app:line_required")
        
        try:
            customer = Customer.objects.get(line_id=line_id)
            request.customer = customer
            return super().dispatch(request, *args, **kwargs)
        except Customer.DoesNotExist:
            messages.error(request, "LINEユーザーが見つかりません。")
            return redirect("app:line_required")






# ショップ一覧（顧客向け）
class IndexView(LineUserRequiredMixin, View):
    def get(self, request):
        shops = Shop.objects.filter(is_active=True).order_by("name")
        return render(request, "app/index.html", {"shops": shops})


# ショップ詳細（顧客向け）
class ShopDetailView(LineUserRequiredMixin, View):
    def get(self, request, shop_id):
        shop = get_object_or_404(Shop, id=shop_id, is_active=True)
        products = shop.products.filter(is_available=True).order_by("category", "name")
        
        # カテゴリ別に商品をグループ化
        products_by_category = {}
        for product in products:
            if product.category not in products_by_category:
                products_by_category[product.category] = []
            products_by_category[product.category].append(product)
        
        # カート情報も取得
        cart, created = Cart.objects.get_or_create(customer=request.customer)
        
        return render(
            request,
            "app/shop_detail.html",
            {
                "shop": shop,
                "products_by_category": products_by_category,
                "cart": cart,
            },
        )


# 管理者チェック
def check_superuser(request):
    if not request.user.is_superuser:
        messages.error(request, "管理者権限が必要です")
        return redirect("app:index")
    return None


# ショップ登録（管理者用）
class ShopRegisterView(LoginRequiredMixin, View):
    def get(self, request):
        if check_superuser(request):
            return redirect("app:index")
        
        form = ShopRegisterForm()
        return render(request, "app/shop_register.html", {"form": form})

    def post(self, request):
        if check_superuser(request):
            return redirect("app:index")
        
        form = ShopRegisterForm(request.POST, request.FILES)
        if form.is_valid():
            shop = form.save(commit=False)
            shop.user = request.user
            shop.save()
            messages.success(request, "ショップを登録しました")
            return redirect("app:index")
        
        return render(request, "app/shop_register.html", {"form": form})


# 商品登録（管理者用）
class ProductRegisterView(LoginRequiredMixin, View):
    def get(self, request):
        if check_superuser(request):
            return redirect("app:index")
        
        shop_id = request.GET.get("shop_id")
        form = ProductRegisterForm()
        
        if shop_id:
            # 特定のショップが選択された状態でフォームを表示
            try:
                shop = Shop.objects.get(id=shop_id)
                form.initial = {'shop': shop}
                context = {"form": form, "selected_shop": shop}
            except Shop.DoesNotExist:
                context = {"form": form}
        else:
            context = {"form": form}
        
        return render(request, "app/product_register.html", context)

    def post(self, request):
        if check_superuser(request):
            return redirect("app:index")
        
        form = ProductRegisterForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, "商品を登録しました")
            return redirect("app:product_manage", shop_id=product.shop.id)
        
        return render(request, "app/product_register.html", {"form": form})


# ショップ管理（管理者用）
class ShopManageView(LoginRequiredMixin, View):
    def get(self, request):
        if check_superuser(request):
            return redirect("app:index")
        
        shops = Shop.objects.all().order_by("-created_at")
        return render(request, "app/shop_manage.html", {"shops": shops})


# 商品管理（管理者用）
class ProductManageView(LoginRequiredMixin, View):
    def get(self, request, shop_id):
        if check_superuser(request):
            return redirect("app:index")
        
        shop = get_object_or_404(Shop, id=shop_id)
        products = Product.objects.filter(shop=shop).order_by('category', 'name')
        
        context = {
            "products": products,
            "filtered_shop": shop,
        }
        return render(request, "app/product_manage.html", context)


# 注文管理（管理者用）
class OrderManageView(LoginRequiredMixin, View):
    def get(self, request):
        if check_superuser(request):
            return redirect("app:index")
        
        orders = Order.objects.all().order_by("-created_at")
        return render(request, "app/order_manage.html", {"orders": orders})

    def post(self, request):
        if check_superuser(request):
            return redirect("app:index")
        
        order_id = request.POST.get("order_id")
        new_status = request.POST.get("status")
        
        if order_id and new_status:
            order = get_object_or_404(Order, id=order_id)
            order.status = new_status
            order.save()
            messages.success(request, f"注文ステータスを{order.get_status_display()}に更新しました")
        
        return redirect("app:order_manage")


# 注文詳細（管理者用）
class OrderDetailView(LoginRequiredMixin, View):
    def get(self, request, order_id):
        if check_superuser(request):
            return redirect("app:index")
        
        order = get_object_or_404(Order, id=order_id)
        return render(request, "app/order_detail.html", {"order": order})


# カート表示（顧客向け）
class CartView(LineUserRequiredMixin, View):
    def get(self, request):
        cart, created = Cart.objects.get_or_create(customer=request.customer)
        
        # カートに商品がある場合は、その商品のショップIDを取得
        shop_id = None
        if cart.items.exists():
            shop_id = cart.items.first().product.shop.id
        
        return render(request, "app/cart.html", {"cart": cart, "shop_id": shop_id})

    def post(self, request):
        action = request.POST.get("action")
        
        if action == "add_to_cart":
            product_id = request.POST.get("product_id")
            quantity = int(request.POST.get("quantity", 1))
            
            try:
                product = Product.objects.get(id=product_id, is_available=True)
                cart, created = Cart.objects.get_or_create(customer=request.customer)
                
                # 既存のカートアイテムを確認
                cart_item, created = CartItem.objects.get_or_create(
                    cart=cart, product=product, defaults={"quantity": quantity}
                )
                
                if not created:
                    cart_item.quantity += quantity
                    cart_item.save()
                
                messages.success(request, f"{product.name}をカートに追加しました")
                
                # カートに追加後は商品詳細ページに戻る
                line_id = request.GET.get('line_id')
                return redirect(build_url_with_line_id('app:shop_detail', line_id, shop_id=product.shop.id))
                
            except Product.DoesNotExist:
                messages.error(request, "商品が見つかりません")
                line_id = request.GET.get('line_id')
                return redirect(build_url_with_line_id('app:index', line_id))
        
        elif action == "update_quantity":
            item_id = request.POST.get("item_id")
            quantity = int(request.POST.get("quantity", 1))
            
            try:
                cart_item = CartItem.objects.get(id=item_id, cart__customer=request.customer)
                if quantity > 0:
                    cart_item.quantity = quantity
                    cart_item.save()
                    messages.success(request, "数量を更新しました")
                else:
                    cart_item.delete()
                    messages.success(request, "商品を削除しました")
            except CartItem.DoesNotExist:
                messages.error(request, "カートアイテムが見つかりません")
            
            line_id = request.GET.get('line_id')
            return redirect(build_url_with_line_id('app:cart', line_id))
        
        elif action == "remove_item":
            item_id = request.POST.get("item_id")
            
            try:
                cart_item = CartItem.objects.get(id=item_id, cart__customer=request.customer)
                cart_item.delete()
                messages.success(request, "商品を削除しました")
            except CartItem.DoesNotExist:
                messages.error(request, "カートアイテムが見つかりません")
            
            line_id = request.GET.get('line_id')
            return redirect(build_url_with_line_id('app:cart', line_id))
        
        line_id = request.GET.get('line_id')
        return redirect(build_url_with_line_id('app:cart', line_id))


# 注文確認（顧客向け）
class OrderConfirmView(LineUserRequiredMixin, View):
    def get(self, request):
        try:
            cart = Cart.objects.get(customer=request.customer)
            if not cart.items.exists():
                messages.error(request, "カートが空です")
                line_id = request.GET.get('line_id')
                return redirect(build_url_with_line_id('app:cart', line_id))
            
            return render(request, "app/order_confirm.html", {"cart": cart})
        except Cart.DoesNotExist:
            messages.error(request, "カートが見つかりません")
            line_id = request.GET.get('line_id')
            return redirect(build_url_with_line_id('app:index', line_id))

    def post(self, request):
        try:
            cart = Cart.objects.get(customer=request.customer)
            if not cart.items.exists():
                messages.error(request, "カートが空です")
                line_id = request.GET.get('line_id')
                return redirect(build_url_with_line_id('app:cart', line_id))
            
            # 注文を作成
            order = Order.objects.create(
                customer=request.customer,
                shop=cart.items.first().product.shop,
                total_amount=cart.total_price,
                note=request.POST.get("note", ""),
            )
            
            # 注文アイテムを作成
            for cart_item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price=cart_item.product.price,
                )
            
            # カートをクリア
            cart.items.all().delete()
            
            messages.success(request, "注文が完了しました")
            line_id = request.GET.get('line_id')
            return redirect(build_url_with_line_id('app:order_complete', line_id, order_id=order.id))
            
        except Cart.DoesNotExist:
            messages.error(request, "カートが見つかりません")
            line_id = request.GET.get('line_id')
            return redirect(build_url_with_line_id('app:index', line_id))


# 注文完了（顧客向け）
class OrderCompleteView(LineUserRequiredMixin, View):
    def get(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id, customer=request.customer)
            return render(request, "app/order_complete.html", {"order": order})
        except Order.DoesNotExist:
            messages.error(request, "注文が見つかりません")
            return redirect(f"app:index?line_id={request.GET.get('line_id')}")


# 注文履歴（顧客向け）
class OrderHistoryView(LineUserRequiredMixin, View):
    def get(self, request):
        orders = Order.objects.filter(customer=request.customer).order_by("-created_at")
        return render(request, "app/order_history.html", {"orders": orders})


# 注文キャンセル（顧客向け）
class OrderCancelView(LineUserRequiredMixin, View):
    def post(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id, customer=request.customer)
            if order.status in ["pending", "preparing"]:
                order.status = "cancelled"
                order.save()
                messages.success(request, "注文をキャンセルしました")
            else:
                messages.error(request, "この注文はキャンセルできません")
        except Order.DoesNotExist:
            messages.error(request, "注文が見つかりません")
        
        return redirect(f"app:order_history?line_id={request.GET.get('line_id')}")


# ショップ編集（管理者用）
class ShopEditView(LoginRequiredMixin, View):
    def get(self, request, shop_id):
        if check_superuser(request):
            return redirect("app:index")
        
        shop = get_object_or_404(Shop, id=shop_id)
        form = ShopRegisterForm(instance=shop)
        return render(request, "app/shop_edit.html", {"form": form, "shop": shop})

    def post(self, request, shop_id):
        if check_superuser(request):
            return redirect("app:index")
        
        shop = get_object_or_404(Shop, id=shop_id)
        form = ShopRegisterForm(request.POST, request.FILES, instance=shop)
        if form.is_valid():
            form.save()
            messages.success(request, "ショップ情報を更新しました")
            return redirect("app:shop_manage")
        
        return render(request, "app/shop_edit.html", {"form": form, "shop": shop})


# 商品編集（管理者用）
class ProductEditView(LoginRequiredMixin, View):
    def get(self, request, product_id):
        if check_superuser(request):
            return redirect("app:index")
        
        product = get_object_or_404(Product, id=product_id)
        form = ProductRegisterForm(instance=product)
        return render(request, "app/product_edit.html", {"form": form, "product": product})

    def post(self, request, product_id):
        if check_superuser(request):
            return redirect("app:index")
        
        product = get_object_or_404(Product, id=product_id)
        form = ProductRegisterForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, "商品情報を更新しました")
            # 正しい形式でリダイレクト
            return redirect("app:product_manage", shop_id=product.shop.id)
        
        return render(request, "app/product_edit.html", {"form": form, "product": product})

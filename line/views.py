from datetime import datetime, timedelta
import re
import json
import requests

from django.conf import settings
from django.http.response import (
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseServerError,
)

from line.forms import CustomerForm

from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views import View
from django.contrib import messages
from app.models import Shop, Product, Cart, CartItem, Order, OrderItem, Customer

from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt


from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import (
    FollowEvent,
    MessageEvent,
    PostbackEvent,
    TextMessage,
    UnfollowEvent,
)


def build_url_with_line_id(view_name, line_id=None, **kwargs):
    """URLを構築し、line_idクエリパラメータを追加するヘルパー関数"""
    url = reverse(view_name, kwargs=kwargs)
    if line_id:
        url += f"?line_id={line_id}"
    return url


def send_line_message(line_id, message_text):
    """LINEメッセージを送信するヘルパー関数"""
    try:
        # LINE Messaging APIのエンドポイント
        url = "https://api.line.me/v2/bot/message/push"
        
        # ヘッダー設定
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {settings.CHANNEL_ACCESS_TOKEN}"
        }
        
        # メッセージデータ
        data = {
            "to": line_id,
            "messages": [
                {
                    "type": "text",
                    "text": message_text
                }
            ]
        }
        
        # APIリクエスト送信
        response = requests.post(url, headers=headers, data=json.dumps(data))
        
        if response.status_code == 200:
            print(f"✅ LINEメッセージ送信成功: {line_id}")
            return True
        else:
            print(f"❌ LINEメッセージ送信失敗: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ LINEメッセージ送信エラー: {str(e)}")
        return False


def create_order_message(order):
    """注文内容をLINEメッセージ用のテキストに変換するヘルパー関数"""
    shop_name = order.shop.name
    order_id = order.id
    total_amount = order.total_amount
    
    # 注文商品の詳細
    items_text = ""
    for item in order.items.all():
        items_text += f"• {item.product.name} × {item.quantity} = ¥{item.subtotal}\n"
    
    # 注文メッセージの作成
    message = f"""注文が確定しました！

注文番号: #{order_id}

注文内容:
{items_text}
合計金額: ¥{total_amount}

ご注文ありがとうございます！
後ほど完成予定時間をお知らせいたします。"""
    
    return message


# LINE認証が必要なページ
class LineRequiredView(View):
    def get(self, request):
        return render(request, "line/line_required.html")


# LINEユーザーのみアクセス可能にするミックスイン
class LineLoginRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        # URLパラメータからline_idを取得
        line_id = request.GET.get("line_id")
        
        # line_idがない場合は、LINE認証が必要ページにリダイレクト
        if not line_id:
            return redirect("line:line_required")
        
        try:
            customer = Customer.objects.get(line_id=line_id)
        except Customer.DoesNotExist:
            # 本番でも初回アクセスで自動登録
            customer = Customer.objects.create(line_id=line_id)
        request.customer = customer
        request.line_id = line_id
        
        return super().dispatch(request, *args, **kwargs)





# LINEアプリのメインページ
class IndexView(View):
    def get(self, request):
        shops = Shop.objects.filter(is_active=True).order_by("name")
        line_id = request.GET.get("line_id")
        liff_id = "2007902301-b7xL87yd"  # 環境変数から取得
        
        print(f"🔍 デバッグ情報 shops変数の長さ: {len(shops)} line_id: {line_id or '未設定'} liff_id: {liff_id}")
        print(f"全ショップ数: {Shop.objects.count()}")
        print(f"アクティブショップ数: {shops.count()}")
        
        return render(
            request,
            "line/index.html",
            {
                "shops": shops,
                "line_id": line_id,
                "liff_id": liff_id,
            },
        )


# 商品一覧（LINE用）
class ProductView(LineLoginRequiredMixin, View):
    def get(self, request, shop_id):
        # customerがNoneの場合は、LINE認証が必要ページにリダイレクト
        if not request.customer:
            return redirect("line:line_required")
        
        shop = get_object_or_404(Shop, id=shop_id)
        products = shop.products.filter(is_available=True).order_by("category", "name")
        cart = Cart.objects.filter(customer=request.customer).first()
        liff_id = "2007902301-b7xL87yd"  # 環境変数から取得
        
        # セッションに最後にアクセスしたショップIDを保存
        request.session['last_shop_id'] = shop_id
        
        return render(
            request,
            "line/product.html",
            {
                "shop": shop,
                "products": products,
                "line_id": request.line_id,
                "cart": cart,
                "liff_id": liff_id,
            },
        )


# カート表示・管理（LINE用）
class CartView(LineLoginRequiredMixin, View):
    def get(self, request):
        # customerがNoneの場合は、LINE認証が必要ページにリダイレクト
        if not request.customer:
            return redirect("line:line_required")
        
        cart, created = Cart.objects.get_or_create(customer=request.customer)
        
        # カートに商品がある場合は、その商品のショップIDを取得
        shop_id = None
        if cart.items.exists():
            shop_id = cart.items.first().product.shop.id
        else:
            # カートが空の場合は、セッションから最後にアクセスしたショップIDを取得
            shop_id = request.session.get('last_shop_id')
        
        liff_id = "2007902301-b7xL87yd"  # 環境変数から取得
        
        return render(request, "line/cart.html", {"cart": cart, "shop_id": shop_id, "line_id": request.line_id, "liff_id": liff_id})

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
                return redirect(build_url_with_line_id("line:product", request.line_id, shop_id=product.shop.id))
                
            except Product.DoesNotExist:
                messages.error(request, "商品が見つかりません")
                return redirect(build_url_with_line_id("line:index", request.line_id))
        
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
            
            return redirect(build_url_with_line_id("line:cart", request.line_id))
        
        elif action == "remove_item":
            item_id = request.POST.get("item_id")
            
            try:
                cart_item = CartItem.objects.get(id=item_id, cart__customer=request.customer)
                cart_item.delete()
                messages.success(request, "商品を削除しました")
            except CartItem.DoesNotExist:
                messages.error(request, "カートアイテムが見つかりません")
            
            return redirect(build_url_with_line_id("line:cart", request.line_id))
        
        return redirect(build_url_with_line_id("line:cart", request.line_id))


# 注文確認（LINE用）
class OrderConfirmView(LineLoginRequiredMixin, View):
    def get(self, request):
        try:
            cart = Cart.objects.get(customer=request.customer)
            if not cart.items.exists():
                messages.error(request, "カートが空です")
                return redirect(build_url_with_line_id("line:cart", request.line_id))
            
            return render(request, "line/order_confirm.html", {"cart": cart, "line_id": request.line_id})
        except Cart.DoesNotExist:
            messages.error(request, "カートが見つかりません")
            return redirect(build_url_with_line_id("line:index", request.line_id))

    def post(self, request):
        try:
            cart = Cart.objects.get(customer=request.customer)
            if not cart.items.exists():
                messages.error(request, "カートが空です")
                return redirect(build_url_with_line_id("line:cart", request.line_id))
            
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
            
            # LINEメッセージを送信
            order_message = create_order_message(order)
            send_line_message(request.line_id, order_message)
            
            messages.success(request, "注文が完了しました")
            return redirect(build_url_with_line_id("line:order_complete", request.line_id, order_id=order.id))
            
        except Cart.DoesNotExist:
            messages.error(request, "カートが見つかりません")
            return redirect(build_url_with_line_id("line:index", request.line_id))


# 注文完了（LINE用）
class OrderCompleteView(LineLoginRequiredMixin, View):
    def get(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id, customer=request.customer)
            return render(request, "line/order_complete.html", {"order": order, "line_id": request.line_id})
        except Order.DoesNotExist:
            messages.error(request, "注文が見つかりません")
            return redirect(build_url_with_line_id("line:index", request.line_id))


# 注文履歴（LINE用）
class OrderHistoryView(LineLoginRequiredMixin, View):
    def get(self, request):
        orders = Order.objects.filter(customer=request.customer).order_by("-created_at")
        return render(request, "line/order_history.html", {"orders": orders, "line_id": request.line_id})


# 注文キャンセル（LINE用）
class OrderCancelView(LineLoginRequiredMixin, View):
    def post(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id, customer=request.customer)
            if order.status in ["pending", "preparing"]:
                order.status = "cancelled"
                order.save()
                
                # キャンセル通知をLINEに送信
                cancel_message = f"""🚫 注文がキャンセルされました

ショップ: {order.shop.name}
注文番号: #{order.id}
金額: ¥{order.total_amount}

注文のキャンセルが完了しました。"""
                
                send_line_message(request.line_id, cancel_message)
                messages.success(request, "注文をキャンセルしました")
            else:
                messages.error(request, "この注文はキャンセルできません")
        except Order.DoesNotExist:
            messages.error(request, "注文が見つかりません")
        
        return redirect(build_url_with_line_id("line:order_history", request.line_id))






line_bot_api = LineBotApi(settings.CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(settings.CHANNEL_SECRET)
# LINE API コールバック
# LINEコールバック
class CallbackView(View):
    def get(self, request):
        return HttpResponse("OK")

    def post(self, request):
        signature = request.META["HTTP_X_LINE_SIGNATURE"]
        body = request.body.decode("utf-8")

        try:
            handler.handle(body, signature)
        except InvalidSignatureError:
            return HttpResponseBadRequest()
        except LineBotApiError as e:
            print(e)
            return HttpResponseServerError()

        return HttpResponse("OK")

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(CallbackView, self).dispatch(*args, **kwargs)

    # 友達追加
    @handler.add(FollowEvent)
    def handle_follow(event):
        line_id = event.source.user_id

        # 既存のユーザーをチェック
        if not Customer.objects.filter(line_id=line_id).exists():
            try:
                # LINEユーザー情報を取得
                profile = line_bot_api.get_profile(line_id)
                # LINEユーザー名
                name = profile.display_name

                # 顧客登録
                Customer.objects.create(name=name, line_id=line_id)
                print("新しい友達追加: ", name)
            except LineBotApiError as e:
                print("新しい友達追加エラー: ", e)
        else:
            print("ユーザーはすでに登録されています。")

    # 友達解除
    @handler.add(UnfollowEvent)
    def handle_unfollow(event):
        line_id = event.source.user_id
        # 対応する顧客を見つけて削除
        try:
            user = Customer.objects.get(line_id=line_id)
            user.delete()
            print("友達解除されたユーザーを削除しました: ", line_id)
        except Customer.DoesNotExist:
            print("削除するユーザーが見つかりませんでした。", line_id)

    # テキストメッセージ
    @handler.add(MessageEvent, message=TextMessage)
    def text_message(event):
        print(event.message.text)

    # ポストバック
    @handler.add(PostbackEvent)
    def on_postback(event):
        pass



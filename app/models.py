from django.db import models
from accounts.models import UserAccount


# ショップ
class Shop(models.Model):
    user = models.OneToOneField(
        UserAccount,
        on_delete=models.CASCADE,
        related_name="shop_profile",
        verbose_name="ショップアカウント",
    )
    name = models.CharField(verbose_name="ショップ名", max_length=100)
    address = models.CharField(
        verbose_name="住所", max_length=200, null=True, blank=True
    )
    tel = models.CharField(
        verbose_name="電話番号", max_length=100, null=True, blank=True
    )
    description = models.TextField(verbose_name="詳細", null=True, blank=True)
    image = models.ImageField(
        upload_to="shop/", verbose_name="画像", null=True, blank=True
    )
    logo = models.ImageField(
        upload_to="shop/logos/", verbose_name="ロゴ", null=True, blank=True
    )
    is_active = models.BooleanField(verbose_name="営業中", default=True)
    open_time = models.TimeField(verbose_name="開店時間", default="09:00:00")
    close_time = models.TimeField(verbose_name="閉店時間", default="21:00:00")

    updated_at = models.DateTimeField("更新日", auto_now=True)
    created_at = models.DateTimeField("作成日", auto_now_add=True)

    class Meta:
        verbose_name = "ショップ"
        verbose_name_plural = "ショップ"

    def __str__(self):
        return self.name


# 商品（ドリンク）
class Product(models.Model):
    CATEGORY_CHOICES = (
        ("food", "フード"),
        ("drink", "ドリンク"),
    )
    
    shop = models.ForeignKey(
        Shop, on_delete=models.CASCADE, verbose_name="ショップ", related_name="products"
    )
    name = models.CharField(max_length=255, verbose_name="商品名")
    category = models.CharField(
        max_length=20, verbose_name="カテゴリ", choices=CATEGORY_CHOICES, default="drink"
    )
    description = models.TextField(verbose_name="詳細", blank=True, null=True)
    price = models.IntegerField(verbose_name="価格")
    image = models.ImageField(
        upload_to="products/", verbose_name="画像", blank=True, null=True
    )
    is_available = models.BooleanField(verbose_name="販売中", default=True)
    stock = models.IntegerField(verbose_name="在庫数", default=999)

    updated_at = models.DateTimeField("更新日", auto_now=True)
    created_at = models.DateTimeField("作成日", auto_now_add=True)

    class Meta:
        verbose_name = "商品"
        verbose_name_plural = "商品"

    def __str__(self):
        return f"{self.shop.name} - {self.name}"


# 顧客
class Customer(models.Model):
    GENDER_CHOICES = (
        ("male", "男性"),
        ("female", "女性"),
        ("other", "その他"),
    )

    name = models.CharField(max_length=255, verbose_name="名前")
    gender = models.CharField(
        max_length=10,
        verbose_name="性別",
        choices=GENDER_CHOICES,
        blank=True,
        null=True,
    )
    phone_number = models.CharField(
        max_length=15, verbose_name="電話番号", blank=True, null=True
    )
    line_id = models.CharField(max_length=255, unique=True, verbose_name="LINE ID")

    updated_at = models.DateTimeField("更新日", auto_now=True)
    created_at = models.DateTimeField("作成日", auto_now_add=True)

    class Meta:
        verbose_name = "顧客"
        verbose_name_plural = "顧客"

    def __str__(self):
        return self.name


# カート
class Cart(models.Model):
    customer = models.OneToOneField(
        Customer, on_delete=models.CASCADE, verbose_name="顧客", related_name="cart"
    )
    created_at = models.DateTimeField("作成日", auto_now_add=True)
    updated_at = models.DateTimeField("更新日", auto_now=True)

    class Meta:
        verbose_name = "カート"
        verbose_name_plural = "カート"

    def __str__(self):
        return f"{self.customer.name}のカート"

    @property
    def total_price(self):
        return sum(item.subtotal for item in self.items.all())

    @property
    def item_count(self):
        return sum(item.quantity for item in self.items.all())


# カートアイテム
class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart, on_delete=models.CASCADE, verbose_name="カート", related_name="items"
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, verbose_name="商品"
    )
    quantity = models.IntegerField(verbose_name="数量", default=1)
    created_at = models.DateTimeField("作成日", auto_now_add=True)

    class Meta:
        verbose_name = "カートアイテム"
        verbose_name_plural = "カートアイテム"
        unique_together = ["cart", "product"]

    def __str__(self):
        return f"{self.cart.customer.name} - {self.product.name} x {self.quantity}"

    @property
    def subtotal(self):
        return self.product.price * self.quantity


# 注文
class Order(models.Model):
    STATUS_CHOICES = (
        ("pending", "受付中"),
        ("preparing", "準備中"),
        ("ready", "準備完了"),
        ("completed", "完了"),
        ("cancelled", "キャンセル"),
    )

    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, verbose_name="顧客", related_name="orders"
    )
    shop = models.ForeignKey(
        Shop, on_delete=models.CASCADE, verbose_name="ショップ", related_name="orders"
    )
    status = models.CharField(
        max_length=20, verbose_name="ステータス", choices=STATUS_CHOICES, default="pending"
    )
    total_amount = models.IntegerField(verbose_name="合計金額")
    note = models.TextField(verbose_name="備考", blank=True, null=True)
    
    created_at = models.DateTimeField("作成日", auto_now_add=True)
    updated_at = models.DateTimeField("更新日", auto_now=True)

    class Meta:
        verbose_name = "注文"
        verbose_name_plural = "注文"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.customer.name} - {self.shop.name} - {self.get_status_display()}"


# 注文アイテム
class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, verbose_name="注文", related_name="items"
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, verbose_name="商品"
    )
    quantity = models.IntegerField(verbose_name="数量")
    price = models.IntegerField(verbose_name="価格")  # 注文時の価格を保存
    created_at = models.DateTimeField("作成日", auto_now_add=True)

    class Meta:
        verbose_name = "注文アイテム"
        verbose_name_plural = "注文アイテム"

    def __str__(self):
        return f"{self.order.id} - {self.product.name} x {self.quantity}"

    @property
    def subtotal(self):
        return self.price * self.quantity

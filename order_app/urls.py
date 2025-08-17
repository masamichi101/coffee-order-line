"""
URL configuration for order_app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('other_app.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.http import HttpResponse

def health_check(request):
    return HttpResponse("OK", status=200)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", health_check, name="health_check"),
    # トップページ
    path("", include("app.urls")),
    # アカウント認証
    path("accounts/", include("accounts.urls")),
    # 認証ライブラリ
    path("accounts/", include("allauth.urls")),
    

    # LINE
    path("line/", include("line.urls")),
]

# メディアファイルのURL設定（開発・本番環境共通）
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
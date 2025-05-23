from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import RedirectView
from django.urls import reverse_lazy

urlpatterns = [
    path('', RedirectView.as_view(url=reverse_lazy('login'))),  # 預設導向登入頁
    path('clock/', include('clock.urls')),                      # 登入成功後導向這裡
    path('stocks/', include('stocks.urls')),
    path('accounts/', include('django.contrib.auth.urls')),     # 提供 /login /logout 等功能
    path('admin/', admin.site.urls),
]

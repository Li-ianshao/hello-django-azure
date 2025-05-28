from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import RedirectView
from django.urls import reverse_lazy

urlpatterns = [
    path('', include('stocks.urls'))
    #path('', RedirectView.as_view(url=reverse_lazy('login'))),  # 預設導向登入頁
    path('stocks/', include('stocks.urls')),
    path('accounts/', include('django.contrib.auth.urls')),     # 提供 /login /logout 等功能
    path('admin/', admin.site.urls),
]

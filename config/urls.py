from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from orders.views import pay_on_delivery, pay_on_livraison, success,health,robots_txt

# Personnalisation dynamique de l'admin
admin.site.site_header = getattr(settings, "ADMIN_SITE_HEADER", "Django Administration")
admin.site.site_title = getattr(settings, "ADMIN_SITE_TITLE", "Admin")
admin.site.index_title = getattr(settings, "ADMIN_INDEX_TITLE", "Bienvenue")
def robots_txt(request):
    content = "User-agent: *\nAllow: /\nSitemap: https://www.maisonfaki.com/sitemap.xml"
    return HttpResponse(content, content_type="text/plain")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('robots.txt', robots_txt),
    path('', include('core.urls')),
    path('products/', include('products.urls')),
    path('cart/', include('cart.urls')),
    path('orders/', include('orders.urls')),
    path('cart/pay-on-delivery/', pay_on_delivery, name='pay_on_delivery'),
    path('cart/pay-on-livraison/', pay_on_livraison, name='pay_on_livraison'),
    path('health/', health, name='health'),
]

# Servir les fichiers statiques et médias en développement
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

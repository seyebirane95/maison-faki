from django.urls import path
from . import views

urlpatterns = [
    path('checkout/', views.checkout, name='checkout'),
    path('success/', views.success, name='success'),
    path('pay-on-delivery/', views.pay_on_delivery, name='pay_on_delivery'),
    path('pay-on-livraison/', views.pay_on_livraison, name='pay_on_livraison'),
    path('payement_par_cartBancaire/', views.payement_par_cartBancaire, name='payement_par_cartBancaire'),
]

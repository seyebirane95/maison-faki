from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages
from products.models import Product
import stripe
from django.conf import settings
from django.shortcuts import redirect

def _get_cart(session):
    return session.setdefault('cart', {})

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    cart = _get_cart(request.session)
    item = cart.get(str(product_id), {'name': product.name, 'price': float(product.price), 'qty': 0})
    if product.stock <= item['qty']:
        messages.warning(request, "Stock insuffisant.")
    else:
        item['qty'] += 1
        cart[str(product_id)] = item
        request.session.modified = True
        messages.success(request, f"{product.name} ajouté au panier.")
    return redirect('product_detail', slug=product.slug)

def remove_from_cart(request, product_id):
    cart = _get_cart(request.session)
    if str(product_id) in cart:
        del cart[str(product_id)]
        request.session.modified = True
        messages.info(request, "Article retiré du panier.")
    return redirect('view_cart')

def update_quantity(request, product_id):
    qty = int(request.POST.get('qty', 1))
    cart = _get_cart(request.session)
    if str(product_id) in cart:
        cart[str(product_id)]['qty'] = max(1, qty)
        request.session.modified = True
    return redirect('view_cart')

def clear_cart(request):
    request.session['cart'] = {}
    request.session.modified = True
    messages.info(request, "Panier vidé.")
    return redirect('view_cart')

def view_cart(request):
    cart = request.session.get('cart', {})
    return render(request, 'cart/view.html', {'cart': cart})

def pay_on_delivery(request):
    cart = request.session.get('cart', {})
    if not cart:
        messages.info(request, "Votre panier est vide.")
        return redirect('view_cart')  # reste sur la page du panier

    # Vider le panier pour simuler la validation de commande
    request.session['cart'] = {}
    request.session.modified = True

    # Rediriger vers la page de succès
    return redirect('/orders/success/')  # '/orders/success/'


stripe.api_key = settings.STRIPE_SECRET_KEY

def payement_par_cartBancaire(request):
    cart = request.session.get('cart', {})

    if not cart:
        messages.warning(request, "Votre panier est vide.")
        return redirect('view_cart')

    line_items = []

    for item in cart.values():
        line_items.append({
            'price_data': {
                'currency': 'eur',
                'product_data': {
                    'name': item['name'],
                },
                'unit_amount': int(float(item['price']) * 100),  # en centimes
            },
            'quantity': item['qty'],
        })

    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=line_items,
        mode='payment',
        success_url='http://localhost:8000/orders/success/',
        cancel_url='http://localhost:8000/view-cart',
    )

    return redirect(session.url)
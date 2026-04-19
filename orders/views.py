from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages
from products.models import Product
from .models import Order, OrderItem  # si tu veux créer des commandes réelles
import stripe
from django.conf import settings
from django.shortcuts import redirect

stripe.api_key = settings.STRIPE_SECRET_KEY


# --- Gestion du panier ---
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

# --- Checkout classique ---
def checkout(request):
    cart = request.session.get('cart', {})
    total = sum(item['price'] * item['qty'] for item in cart.values())

    if request.method == "POST":
        # récupérer infos du formulaire
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        address = request.POST.get('address')
        phone = request.POST.get('phone')
        email = request.POST.get('email')

        if not cart:
            messages.error(request, "Votre panier est vide.")
            return redirect('product_list')

        # Calculer total_amount
        total_amount = sum(item['price'] * item['qty'] for item in cart.values())

        # Créer la commande
        order = Order.objects.create(
            first_name=first_name,
            last_name=last_name,
            address=address,
            phone=phone,
            email=email,
            payment_method="qr_code",
            total_amount=total_amount
        )

        # Créer les items
        for pid, item in cart.items():
            OrderItem.objects.create(
                order=order,
                product_id=int(pid),
                quantity=item['qty'],
                price=item['price']
            )

        # vider le panier
        request.session['cart'] = {}
        request.session.modified = True

        # rediriger vers le paiement QR code
        return redirect('wave_payment', order_id=order.id)

    return render(request, 'orders/checkout.html', {
        'cart': cart,
        'total': total
    })


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Order, OrderItem





# --- Paiement après livraison ---
def pay_on_delivery(request):
    cart = request.session.get('cart', {})
    if not cart:
        messages.info(request, "Votre panier est vide.")
        return redirect('view_cart')

    if request.method == 'POST':
        # Récupération des infos client depuis le formulaire
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        email = request.POST.get('email', '')
        address = request.POST.get('address', '')
        phone = request.POST.get('phone', '')

        total = sum(item['qty'] * float(item['price']) for item in cart.values())

        # Création de la commande
        order = Order.objects.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            address=address,
            phone=phone,
            total_amount=total,
            status='pending'  # Assurez-vous que le champ status existe dans Order
        )

        # Création des OrderItem
        for pid, item in cart.items():
            product = Product.objects.get(id=pid)
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=item['qty'],
                price=item['price']
            )

        # Vider le panier après création de la commande
        request.session['cart'] = {}
        request.session.modified = True

        messages.success(request, "Votre commande a été passée avec succès. Vous payerez à la livraison.")
        return redirect('success')  # page de confirmation
    total = sum(item['qty'] * item['price'] for item in cart.values())
    return render(request, 'orders/checkout.html', {
        'cart': cart,
        'total': total
    })
    #return render(request, 'orders/checkout.html', {'cart': cart})


from django.shortcuts import render


def cancel(request):
    return render(request, 'orders/cancel.html')


def successold(request):
    cart = request.session.get('cart', {})
    checkout_data = request.session.get('checkout_data', {})

    if cart and checkout_data:
        order = Order.objects.create(
            first_name=checkout_data["first_name"],
            last_name=checkout_data["last_name"],
            email=checkout_data["email"],
            address=checkout_data["address"],
            phone=checkout_data["phone"],
            payment_method="card",
            payment_status="payer",
            total_amount=0
        )

        request.session['cart'] = {}
        request.session['checkout_data'] = {}

    return render(request, 'orders/success.html')



def pay_on_livraison(request):
    cart = request.session.get('cart', {})

    if not cart:
        messages.info(request, "Votre panier est vide.")
        return redirect('view_cart')

    total = sum(item['qty'] * float(item['price']) for item in cart.values())

    if request.method == "POST":
        # récupérer infos du formulaire
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        address = request.POST.get('address')
        phone = request.POST.get('phone')

        # créer la commande
        order = Order.objects.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            address=address,
            phone=phone,
            payment_method="cash",  # paiement à la livraison
            payment_status="pending",  # pas encore payé
            total_amount=total
        )

        # ajouter les produits commandés
        for pid, item in cart.items():
            OrderItem.objects.create(
                order=order,
                product_id=int(pid),
                quantity=item['qty'],
                price=item['price']
            )

        # vider le panier
        request.session['cart'] = {}
        request.session.modified = True

        # rediriger vers page succès
        return redirect('success')

    return render(request, 'orders/pay_on_delivery.html', {
        'cart': cart,
        'total': total
    })



stripe.api_key = settings.STRIPE_SECRET_KEY





def payement_par_cartBancaire(request):
    if request.method == "POST":

        cart = request.session.get('cart', {})

        if not cart:
            messages.warning(request, "Votre panier est vide.")
            return redirect('view_cart')

        # Infos client
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        address = request.POST.get('address')
        phone = request.POST.get('phone')

        total_amount = sum(
            float(item['price']) * item['qty'] for item in cart.values()
        )

        # ✅ Créer commande
        order = Order.objects.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            address=address,
            phone=phone,
            payment_method="card",
            payment_status="pending",
            total_amount=total_amount
        )

        # Stripe items
        line_items = []
        for item in cart.values():
            line_items.append({
                'price_data': {
                    'currency': 'eur',
                    'product_data': {
                        'name': item['name'],
                    },
                    'unit_amount': int(float(item['price']) * 100),
                },
                'quantity': item['qty'],
            })
 # vider le panier
        request.session['cart'] = {}
        request.session.modified = True


        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            customer_email=email,

            metadata={
                "order_id": order.id
            },

            # 🔥 IMPORTANT : on passe session_id
            success_url='http://127.0.0.1:8000/orders/success/',
            cancel_url='http://127.0.0.1:8000/orders/cancel/',
        )

        order.stripe_session_id = session.id
        order.save()
         # Vider le panier après création de la commande
        

        return redirect(session.url)
        
    return redirect('clear_cart')



def success(request):
    session_id = request.GET.get('session_id')

    if not session_id:
        return render(request, 'orders/success.html', {
            "error": "Session Stripe manquante"
        })

    try:
        # 🔥 Vérifier paiement Stripe
        session = stripe.checkout.Session.retrieve(session_id)

        if session.payment_status == "paid":

            order = Order.objects.get(stripe_session_id=session_id)

            # ✅ éviter double update
            if order.payment_status != "paid":
                order.payment_status = "paid"
                order.save()

                # 🔥 vider panier
                request.session['cart'] = {}

            return render(request, 'orders/success.html', {
                "success": True
            })

        else:
            return render(request, 'orders/success.html', {
                "error": "Paiement non confirmé"
            })

    except Order.DoesNotExist:
        return render(request, 'orders/success.html', {
            "error": "Commande introuvable"
        })

    except Exception as e:
        return render(request, 'orders/success.html', {
            "error": str(e)
        })
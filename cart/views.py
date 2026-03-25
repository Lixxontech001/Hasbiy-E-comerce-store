from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from urllib3 import request

from .models import Cart, CartItem
from django.db.models import Sum
from shop.models import Product
from shop.models import Variation
def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart


from django.http import JsonResponse

def add_cart(request, product_id):
    current_user = request.user
    action = request.POST.get('action')
    product = Product.objects.get(id=product_id)
    
    try:
        qty_to_add = int(request.POST.get('quantity', 1))
    except:
        qty_to_add = 1

    product_variation = []
    if request.method == 'POST':
        for item in request.POST:
            key = item
            value = request.POST[key]
            try:
                variation = Variation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value)
                product_variation.append(variation)
            except:
                pass

    # 1. Get the items (Works for both User and Guest)
    if current_user.is_authenticated:
        cart_items = CartItem.objects.filter(product=product, user=current_user)
    else:
        try:
            cart = Cart.objects.get(cart_id=_cart_id(request))
        except Cart.DoesNotExist:
            cart = Cart.objects.create(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(product=product, cart=cart)

    ex_var_list = [list(item.variation.all()) for item in cart_items]
    id_list = [item.id for item in cart_items]

    # 2. Update or Create
    if product_variation in ex_var_list:
        index = ex_var_list.index(product_variation)
        item_id = id_list[index]
        item = CartItem.objects.get(id=item_id)
        
        # --- CORRECTED LOGIC SPOT ---
        if action == 'increase':
            item.quantity += 1
        elif action == 'decrease':
            if item.quantity > 1:
                item.quantity -= 1
            else:
                item.delete()
                return JsonResponse({'status': 'deleted'})
        else:
            # This is for the normal "Add to Cart" button
            item.quantity += qty_to_add 
        item.save()
    else:
        # Create new item
        if current_user.is_authenticated:
            item = CartItem.objects.create(product=product, quantity=qty_to_add, user=current_user)
        else:
            item = CartItem.objects.create(product=product, quantity=qty_to_add, cart=cart)
            
        if len(product_variation) > 0:
            item.variation.add(*product_variation)
        item.save()

    # 3. THE AJAX RESPONSE (The part that updates your screen)
    # NEW: AJAX Response (No Reload)
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # 1. Get ALL items for the current user/guest to calculate totals
        if current_user.is_authenticated:
            all_items = CartItem.objects.filter(user=current_user, is_active=True)
        else:
            # We need to define 'cart' here for guests
            cart = Cart.objects.get(cart_id=_cart_id(request))
            all_items = CartItem.objects.filter(cart=cart, is_active=True)

        # 2. Calculate the totals correctly
        total_price = sum(i.product.price * i.quantity for i in all_items)
        tax = round(((2 * total_price) / 100), 2)
        count = all_items.count()
        grand_total = float(total_price) + float(tax) + 15.00 # 15 is your handling fee
            
        return JsonResponse({
            'status': 'success',
            'qty': item.quantity,
            'sub_total': item.product.price * item.quantity,
            'total': total_price,
            'vat': tax,
            'cart_count': count,
            'order_total': grand_total
        })
# def add_cart(request, product_id):
#     current_user = request.user
#     product = get_object_or_404(Product, id=product_id)
    
#     # Get requested quantity (default to 1 if not provided)
#     qty_from_post = int(request.POST.get('quantity', 1))
#     action = request.POST.get('action')

#     # 1. Logic for Variations
#     product_variation = []
#     if request.method == 'POST':
#         for item in request.POST:
#             key = item
#             value = request.POST[key]
#             try:
#                 variation = Variation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value)
#                 product_variation.append(variation)
#             except:
#                 pass

#     # 2. Find or Create the Cart Item
#     if current_user.is_authenticated:
#         cart_item, created = CartItem.objects.get_or_create(product=product, user=current_user)
#     else:
#         cart, _ = Cart.objects.get_or_create(cart_id=_cart_id(request))
#         cart_item, created = CartItem.objects.get_or_create(product=product, cart=cart)

#     # 3. Handle Actions (AJAX from Cart Page) or Initial Add (Shop/Details)
#     if action == 'increase':
#         cart_item.quantity += 1
#     elif action == 'decrease':
#         if cart_item.quantity > 1:
#             cart_item.quantity -= 1
#         else:
#             cart_item.delete()
#             return JsonResponse({'status': 'deleted'})
#     else:
#         # This handles the "Add to Basket" button
#         # If it's a fresh add, we set the quantity to what was in the input box
#         if created:
#             cart_item.quantity = qty_from_post
#         else:
#             cart_item.quantity += qty_from_post
    
#     cart_item.save()

#     # 4. JSON Response for AJAX
#     if request.headers.get('x-requested-with') == 'XMLHttpRequest':
#         # Re-calculate totals
#         if current_user.is_authenticated:
#             items = CartItem.objects.filter(user=current_user)
#         else:
#             items = CartItem.objects.filter(cart__cart_id=_cart_id(request))

#         total_price = sum(item.product.price * item.quantity for item in items)
#         tax = round((0.02 * total_price), 2)
#         order_total = float(total_price + tax + 15.00)

#         return JsonResponse({
#             'status': 'success',
#             'qty': cart_item.quantity,
#             'sub_total': cart_item.sub_total(),
#             'total': total_price,
#             'order_total': order_total,
#             'vat': tax
#         })

#     return redirect('cart:cart')


def remove_cart(request, product_id, cart_item_id):
    product = get_object_or_404(Product, id=product_id)
    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
        else:
            cart = Cart.objects.get(cart_id= _cart_id(request))
            cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
        if cart_item.quantity > 1 :
            cart_item.quantity -= 1
            cart_item.save()
        else :
            cart_item.delete()
    except:
        pass

    return redirect('cart:cart')


def remove_cart_item(request, product_id, cart_item_id):
    product = get_object_or_404(Product, id=product_id)
    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
    else:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
    cart_item.delete()
    return redirect('cart:cart')

def cart(request, total_price=0, quantity=0, cart_items=None):
    grand_total = 0
    tax = 0

    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total_price += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
    
    except ObjectDoesNotExist:
        pass
    
    
    tax = round(((2 * total_price)/100), 2)
    grand_total = total_price + tax
    handing = 15.00
    total = float(grand_total) + handing

    context = {
        'total' : total_price,
        'quantity': quantity,
        'cart_items':cart_items,
        'order_total':total,
        'vat' : tax,
        'handing':handing,
    }

    return render(request, 'shop/cart/cart.html', context)


from django.shortcuts import render, get_object_or_404, redirect
from DjangoEcommerceApp.models import Categories, Products, ProductMedia, ProductDetails, ProductAbout, ProductTags
from django.contrib import messages

def home_page(request):
    categories = Categories.objects.filter(is_active=1)
    
    category_product_data = []
    
    for category in categories:
        # Fetch up to 8 products for each category to show in the horizontal slider
        products = Products.objects.filter(subcategories_id__category_id=category, is_active=1).order_by('-id')[:8]
        
        if products.exists():
            product_list = []
            for product in products:
                media = ProductMedia.objects.filter(product_id=product.id, media_type="1", is_active=1).last()
                if not media:
                    media = ProductMedia.objects.filter(product_id=product.id, media_type=1, is_active=1).last()
                    
                product_list.append({
                    'product': product,
                    'media': media
                })
                
            category_product_data.append({
                'category': category,
                'products': product_list
            })

    context = {
        'categories': categories,
        'category_product_data': category_product_data,
    }
    return render(request, "front_templates/home.html", context)

def product_details(request, product_id, product_slug):
    categories = Categories.objects.filter(is_active=1)
    product = get_object_or_404(Products, id=product_id, url_slug=product_slug, is_active=1)
    
    product_media = ProductMedia.objects.filter(product_id=product.id, is_active=1).order_by('-id')
    product_details_list = ProductDetails.objects.filter(product_id=product.id, is_active=1)
    product_about = ProductAbout.objects.filter(product_id=product.id, is_active=1)
    product_tags = ProductTags.objects.filter(product_id=product.id, is_active=1)
    
    context = {
        'categories': categories,
        'product': product,
        'product_media': product_media,
        'product_details_list': product_details_list,
        'product_about': product_about,
        'product_tags': product_tags,
    }
    return render(request, "front_templates/product_details.html", context)

def add_to_cart(request, product_id):
    if request.method == "POST":
        qty = int(request.POST.get("qty", 1))
        
        if 'cart' not in request.session:
            request.session['cart'] = {}
            
        cart = request.session['cart']
        pid = str(product_id)
        
        if pid in cart:
            cart[pid] += qty
        else:
            cart[pid] = qty
            
        request.session['cart'] = cart
        request.session.modified = True
        
        messages.success(request, "Item added to cart successfully!")
        return redirect(request.META.get('HTTP_REFERER', 'home_page'))
        
    return redirect('home_page')

def category_product_list(request, category_slug):
    categories = Categories.objects.filter(is_active=1)
    current_category = get_object_or_404(Categories, url_slug=category_slug, is_active=1)
    
    products = Products.objects.filter(subcategories_id__category_id=current_category, is_active=1).order_by('-id')
    
    product_list = []
    for product in products:
        media = ProductMedia.objects.filter(product_id=product.id, media_type="1", is_active=1).last()
        if not media:
            media = ProductMedia.objects.filter(product_id=product.id, media_type=1, is_active=1).last()
            
        product_list.append({
            'product': product,
            'media': media
        })
        
    context = {
        'categories': categories,
        'current_category': current_category,
        'product_list': product_list,
    }
    return render(request, "front_templates/category_product_list.html", context)

def cart_view(request):
    categories = Categories.objects.filter(is_active=1)
    cart = request.session.get('cart', {})
    
    cart_items = []
    subtotal = 0
    
    for pid, qty in cart.items():
        try:
            product = Products.objects.get(id=pid, is_active=1)
            media = ProductMedia.objects.filter(product_id=product.id, is_active=1).order_by('-id').first()
            
            # Use discount price if available, else max price
            price_str = product.product_discount_price if product.product_discount_price else product.product_max_price
            # Extract numbers from price string if it has currency symbols
            import re
            price_match = re.search(r'[\d\.]+', str(price_str))
            price = float(price_match.group()) if price_match else 0
            
            item_total = price * qty
            subtotal += item_total
            
            cart_items.append({
                'product': product,
                'media': media,
                'qty': qty,
                'price': price,
                'item_total': item_total
            })
        except Products.DoesNotExist:
            continue
            
    # Assuming a flat $10 shipping or tax for placeholder
    tax_shipping = 10 if cart_items else 0
    grand_total = subtotal + tax_shipping
    
    context = {
        'categories': categories,
        'cart_items': cart_items,
        'subtotal': subtotal,
        'tax_shipping': tax_shipping,
        'grand_total': grand_total,
    }
    
    return render(request, "front_templates/cart.html", context)

def update_cart(request, product_id, action):
    if 'cart' in request.session:
        cart = request.session['cart']
        pid = str(product_id)
        
        if pid in cart:
            if action == 'increase':
                cart[pid] += 1
            elif action == 'decrease':
                cart[pid] -= 1
                if cart[pid] <= 0:
                    del cart[pid]
            elif action == 'remove':
                del cart[pid]
                
        request.session['cart'] = cart
        request.session.modified = True
        
    return redirect('cart_view')

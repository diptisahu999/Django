from django.shortcuts import render, get_object_or_404, redirect
from DjangoEcommerceApp.models import Categories, Products, ProductMedia, ProductDetails, ProductAbout, ProductTags
from django.contrib import messages

def home_page(request):
    categories = Categories.objects.filter(is_active=1)
    
    products = Products.objects.filter(is_active=1).order_by('-id')[:12]
    
    product_list = []
    for product in products:
        # Note: media_type choice in models is ((1,"Image"),(2,"Video")), but stored as CharField so might be "1"
        media = ProductMedia.objects.filter(product_id=product.id, media_type="1", is_active=1).first()
        if not media:
            # Fallback to integer 1 just in case
            media = ProductMedia.objects.filter(product_id=product.id, media_type=1, is_active=1).first()
            
        product_list.append({
            'product': product,
            'media': media
        })

    context = {
        'categories': categories,
        'product_list': product_list,
    }
    return render(request, "front_templates/home.html", context)

def product_details(request, product_slug):
    categories = Categories.objects.filter(is_active=1)
    product = get_object_or_404(Products, url_slug=product_slug, is_active=1)
    
    product_media = ProductMedia.objects.filter(product_id=product.id, is_active=1)
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

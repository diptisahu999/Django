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

def product_details(request, product_slug):
    categories = Categories.objects.filter(is_active=1)
    product = get_object_or_404(Products, url_slug=product_slug, is_active=1)
    
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

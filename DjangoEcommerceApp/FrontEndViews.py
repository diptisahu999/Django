from django.shortcuts import render, get_object_or_404, redirect
from DjangoEcommerceApp.models import Categories, Products, ProductMedia, ProductDetails, ProductAbout, ProductTags, CartItem
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
        
        if request.user.is_authenticated:
            try:
                product = Products.objects.get(id=product_id)
                cart_item, created = CartItem.objects.get_or_create(
                    user=request.user,
                    product=product,
                    defaults={'quantity': qty}
                )
                if not created:
                    cart_item.quantity += qty
                    cart_item.save()
            except Products.DoesNotExist:
                pass
        else:
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
    
    cart = {}
    if request.user.is_authenticated:
        db_cart = CartItem.objects.filter(user=request.user)
        for item in db_cart:
            cart[str(item.product.id)] = item.quantity
    else:
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
    if request.user.is_authenticated:
        try:
            cart_item = CartItem.objects.get(user=request.user, product_id=product_id)
            if action == 'increase':
                cart_item.quantity += 1
                cart_item.save()
            elif action == 'decrease':
                cart_item.quantity -= 1
                if cart_item.quantity <= 0:
                    cart_item.delete()
                else:
                    cart_item.save()
            elif action == 'remove':
                cart_item.delete()
        except CartItem.DoesNotExist:
            pass
    else:
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

def signup(request):
    categories = Categories.objects.filter(is_active=1)
    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        
        from DjangoEcommerceApp.models import CustomUser
        try:
            # Create user
            user = CustomUser.objects.create_user(
                username=username, 
                password=password, 
                email=email, 
                first_name=first_name, 
                last_name=last_name, 
                user_type=4
            )
            # The signal in models.py will automatically create the CustomerUser profile
            
            # Log the user in
            from django.contrib.auth import login
            login(request, user)
            
            messages.success(request, "Account created successfully!")
            return redirect('home_page')
            
        except Exception as e:
            messages.error(request, "Error creating account. Username or email might already exist.")
            
    context = {
        'categories': categories,
    }
    return render(request, "front_templates/signup.html", context)

from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage

@login_required(login_url="/admindashboard/admin/")
def profile_view(request):
    categories = Categories.objects.filter(is_active=1)
    user = request.user
    
    if request.method == "POST":
        user.first_name = request.POST.get("first_name")
        user.last_name = request.POST.get("last_name")
        user.email = request.POST.get("email")
        
        password = request.POST.get("password")
        if password:
            user.set_password(password)
            from django.contrib.auth import update_session_auth_hash
            update_session_auth_hash(request, user)
            
        user.save()
        
        if request.FILES.get("profile_pic", False):
            profile_pic = request.FILES["profile_pic"]
            fs = FileSystemStorage()
            filename = fs.save(profile_pic.name, profile_pic)
            profile_pic_url = fs.url(filename)
            
            if str(user.user_type) == "4":
                user.customeruser.profile_pic = profile_pic_url
                user.customeruser.save()
            elif str(user.user_type) == "3":
                user.merchantuser.profile_pic = profile_pic_url
                user.merchantuser.save()
            elif str(user.user_type) == "2":
                user.staffuser.profile_pic = profile_pic_url
                user.staffuser.save()
            elif str(user.user_type) == "1":
                user.adminuser.profile_pic = profile_pic_url
                user.adminuser.save()
                
        messages.success(request, "Profile updated successfully!")
        return redirect('profile_view')
        
    context = {
        'categories': categories,
    }
    return render(request, "front_templates/profile.html", context)

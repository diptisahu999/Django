from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from django.urls import reverse

# Create your views here.
def demoPage(request):
    return HttpResponse("demo Page")

def demoPageTemplate(request):
    return render(request,"demo.html")

def adminLogin(request):
    return render(request,"admin_templates/signin.html")

def adminLoginProcess(request):
    username=request.POST.get("username")
    password=request.POST.get("password")

    from DjangoEcommerceApp.models import CustomUser
    try:
        user_check = CustomUser.objects.get(username=username)
        if not user_check.is_active:
            messages.error(request,"Your account has been deactivated by the admin!")
            return HttpResponseRedirect(reverse("admin_login"))
    except CustomUser.DoesNotExist:
        pass

    user=authenticate(request=request,username=username,password=password)
    if user is not None:
        session_cart = request.session.get('cart', {})
        login(request=request,user=user)
        
        if session_cart:
            from DjangoEcommerceApp.models import CartItem, Products
            for product_id_str, qty in session_cart.items():
                try:
                    product = Products.objects.get(id=int(product_id_str))
                    cart_item, created = CartItem.objects.get_or_create(
                        user=user,
                        product=product,
                        defaults={'quantity': qty}
                    )
                    if not created:
                        cart_item.quantity += qty
                        cart_item.save()
                except Exception:
                    pass
            request.session['cart'] = {}
            request.session.modified = True
            
        if user.user_type == "4":
            return HttpResponseRedirect(reverse("home_page"))
        return HttpResponseRedirect(reverse("admin_home"))
    else:
        messages.error(request,"Error in Login! Invalid Login Details!")
        return HttpResponseRedirect(reverse("admin_login"))

def adminLogoutProcess(request):
    logout(request)
    messages.success(request,"Logout Successfully!")
    return HttpResponseRedirect(reverse("admin_login"))
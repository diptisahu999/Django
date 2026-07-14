from DjangoEcommerceApp.models import CartItem
from django.db.models import Sum

def cart_processor(request):
    cart_count = 0
    if request.user.is_authenticated:
        result = CartItem.objects.filter(user=request.user).aggregate(total_qty=Sum('quantity'))
        if result['total_qty']:
            cart_count = result['total_qty']
    else:
        if 'cart' in request.session:
            try:
                cart_count = sum(int(qty) for qty in request.session['cart'].values())
            except (ValueError, TypeError):
                pass
    return {'cart_count': cart_count}

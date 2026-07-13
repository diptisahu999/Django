def cart_processor(request):
    cart_count = 0
    if 'cart' in request.session:
        # Sum the values (quantities) in the cart dictionary
        try:
            cart_count = sum(int(qty) for qty in request.session['cart'].values())
        except (ValueError, TypeError):
            pass
    return {'cart_count': cart_count}

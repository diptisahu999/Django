from django.shortcuts import render
from DjangoEcommerceApp.models import Categories, Products, ProductMedia

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

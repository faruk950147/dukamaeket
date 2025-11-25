from store.models import Category

def store_context(request):
    categories = Category.objects.filter(parent=None)
    return {
        'categories': categories,
    }

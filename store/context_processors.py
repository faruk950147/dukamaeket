from store.models import Category

def store_context(request):
    # Root categories + prefetch all children for efficiency
    categories = Category.objects.filter(parent=None).prefetch_related(
        'children',              # Level 1
        'children__children'     # Level 2
    )
    return {'categories': categories}

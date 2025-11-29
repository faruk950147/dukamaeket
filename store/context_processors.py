from store.models import Brand, Category

def store_context(request):
    # Root categories + prefetch all children for efficiency
    categories = Category.objects.filter(parent=None, status='active').prefetch_related(
        'children',              # Level 1
        'children__children'     # Level 2
    )
    # distinct used ForeignKey for unique cates
    # cats =  Category.objects.filter(status='active', children__isnull=True).distinct()
    cats =  Category.objects.filter(status='active')
    
    return {'categories': categories, 'cats': cats}

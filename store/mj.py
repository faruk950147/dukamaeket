@method_decorator(never_cache, name='dispatch')
class ProductDetailView(generic.View):
    def get(self, request, slug, id):
        # Main product with related fields
        product = get_object_or_404(
            Product.objects.select_related('category', 'brand')
            .prefetch_related('images', 'reviews', 'variants__color', 'variants__size')
            .annotate(avg_rate=Avg('reviews__rating', filter=Q(reviews__status='active'))),
            slug=slug, id=id, status='active', available_stock__gt=0
        )

        # Related products (same category, exclude current)
        related_products = Product.objects.filter(
            category=product.category, status='active', available_stock__gt=0
        ).exclude(id=product.id)[:4]

        context = {
            'product': product,
            'related_products': related_products,
        }

        # Handle product variants if exists
        if product.variant != "None":
            variants = ProductVariant.objects.filter(
                product_id=id, status='active', available_stock__gt=0
            ).order_by('id')

            if variants.exists():
                # Default variant (first one)
                variant = variants.first()

                # Sizes (distinct)
                sizes = ProductVariant.objects.raw(
                    'SELECT * FROM store_productvariant WHERE product_id=%s GROUP BY size_id',
                    [id]
                )
                # Colors for default size
                colors = ProductVariant.objects.filter(
                    product_id=id,
                    size_id=variant.size_id,
                    status='active',
                    available_stock__gt=0
                )

                context.update({
                    'sizes': sizes,
                    'colors': colors,
                    'variant': variant,
                })
            else:
                # No variants available
                context.update({
                    'sizes': [],
                    'colors': [],
                    'variant': None,
                })

        return render(request, 'store/product-detail.html', context)
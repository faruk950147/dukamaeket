from django.shortcuts import render, get_object_or_404
from django.views import generic
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db.models import Avg, Q
from django.core.paginator import Paginator
from django.http import JsonResponse

from store.models import (
    Category,
    Brand,
    Product,
    Slider,
    AcceptancePayment,
    ProductVariant,
    Review
)

from account.mixing import LogoutRequiredMixin, LoginRequiredMixin

# =========================================================
# HOME PAGE VIEW
# =========================================================
@method_decorator(never_cache, name='dispatch')
class HomeView(generic.View):
    def get(self, request):
        # Fetch all active sliders
        active_sliders = Slider.objects.filter(status='active')
        sliders = active_sliders.filter(Q(slider_type='slider') | Q(slider_type='feature'))

        # Filter sliders by type
        feature_sliders = active_sliders.filter(Q(slider_type='feature'))[:4]
        add_sliders = active_sliders.filter(Q(slider_type='add'))[:2]
        promo_sliders = active_sliders.filter(Q(slider_type='promotion'))[:3]

        # Fetch acceptance payments
        acceptance_payments = AcceptancePayment.objects.filter(status='active')[:4]

        # Fetch featured brands
        brands = Brand.objects.filter(status='active', is_featured=True)

        # Fetch featured categories (leaf categories only)
        cates = Category.objects.filter(status='active', children__isnull=True, is_featured=True)[:3]

        # Fetch top deals products (discounted & active deadline)
        top_deals = list(Product.objects.filter(
            status='active', discount_percent__gt=0, is_deadline=True, deadline__gte=timezone.now()
        ).select_related('category', 'brand')
         .prefetch_related('reviews')
         .annotate(avg_rate=Avg('reviews__rating', filter=Q(reviews__status='active')))
         .order_by('-discount_percent', 'deadline')[:6])

        first_top_deal = top_deals[0] if top_deals else None

        # Fetch featured products
        featured_products = Product.objects.filter(
            status='active', is_featured=True
        ).select_related('category', 'brand').prefetch_related('reviews') \
         .annotate(avg_rate=Avg('reviews__rating', filter=Q(reviews__status='active')))[:5]

        context = {
            'sliders': sliders,
            'feature_sliders': feature_sliders,
            'add_sliders': add_sliders,
            'promo_sliders': promo_sliders,
            'acceptance_payments': acceptance_payments,
            'brands': brands,
            'cates': cates,
            'top_deals': top_deals,
            'first_top_deal': first_top_deal,
            'featured_products': featured_products,
        }

        return render(request, 'store/home.html', context)


# =========================================================
# PRODUCT DETAIL VIEW
# =========================================================
@method_decorator(never_cache, name='dispatch')
class ProductDetailView(generic.View):
    def get(self, request, slug, id):
        # Fetch the main product with related data
        product = get_object_or_404(
            Product.objects.select_related('category', 'brand')
                .prefetch_related('reviews', 'variants__color', 'variants__size', 'images')
                .annotate(avg_rate=Avg('reviews__rating', filter=Q(reviews__status='active'))),
            slug=slug,
            id=id,
            status='active'
        )

        # Fetch default variant (fallback to first if none)
        variant = product.variants.filter(is_default=True).first()
        if not variant:
            variant = product.variants.first()

        # Fetch related products (same category, exclude current)
        related_products = Product.objects.filter(
            category=product.category,
            status='active'
        ).exclude(id=product.id).select_related('category', 'brand') \
         .prefetch_related('reviews').annotate(avg_rate=Avg('reviews__rating', filter=Q(reviews__status='active')))[:4]

        context = {
            'product': product,
            'variant': variant,
            'related_products': related_products
        }

        return render(request, 'store/product-detail.html', context)


# =========================================================
# PRODUCT REVIEW VIEW (AJAX)
# =========================================================
@method_decorator(never_cache, name='dispatch')
class ProductReviewView(LoginRequiredMixin, generic.View):
    def post(self, request):
        user = request.user
        product_id = request.POST.get('product_id')
        rating = request.POST.get('rating')
        subject = request.POST.get('subject')
        comment = request.POST.get('comment')

        if not rating or not rating.isdigit() or not subject or not comment:
            return JsonResponse({'status': 'error', 'message': 'All fields are required and rating must be a number'}, status=400)

        rating = int(rating)
        if rating < 1 or rating > 5:
            return JsonResponse({'status': 'error', 'message': 'Rating must be between 1 and 5'}, status=400)

        product = get_object_or_404(Product, id=product_id, status='active')

        review = Review.objects.create(
            user=user,
            product=product,
            rating=rating,
            subject=subject,
            comment=comment
        )

        review_count = product.reviews.filter(status='active').count()

        image_url = getattr(user.profile, 'image', None)
        image_url = image_url.url if image_url else '/media/defaults/default.jpg'

        review_html = f"""
        <div class="review-details-des">
            <div class="author-image mr-15">
                <img src="{image_url}" alt="{user.username}" style="width: 50px; height: 50px">
            </div>
            <div class="review-details-content">
                <h5>{review.rating:.2f}</h5>
                <div class="str-info">
                    <div class="review-star mr-15">
                        {"".join(['<i class="text-warning fa fa-star"></i>' if i <= review.rating else '<i class="text-warning fa fa-star-o"></i>' for i in range(1, 6)])}
                    </div>
                </div>
                <div class="name-date mb-30">
                    <h6>{user.username} – <span>{review.created_date.strftime('%Y-%m-%d %H:%M')}</span></h6>
                </div>
                <p>{review.subject}</p>
                <p>{review.comment}</p>
            </div>
        </div>
        """

        return JsonResponse({
            'status': 'success',
            'message': 'Review submitted successfully',
            'review_count': review_count,
            'review_html': review_html
        })


# =========================================================
# SHOP VIEW WITH PAGINATION
# =========================================================
@method_decorator(never_cache, name='dispatch')
class ShopView(generic.View):
    def get(self, request):
        # Fetch all active products with related data
        products = Product.objects.filter(status='active').select_related('category', 'brand') \
                         .prefetch_related('reviews').annotate(avg_rate=Avg('reviews__rating', filter=Q(reviews__status='active')))

        # Pagination: 12 products per page
        paginator = Paginator(products, 12)
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)

        context = {
            'page_obj': page_obj
        }

        return render(request, 'store/shop.html', context)


# =========================================================
# AJAX: GET PRODUCT VARIANT PRICE / STOCK / IMAGE
# =========================================================
@method_decorator(csrf_exempt, name='dispatch')
class GetVariantsView(generic.View):
    def post(self, request):
        product_id = request.POST.get('product_id')
        color_id = request.POST.get('color_id')
        size_id = request.POST.get('size_id')

        variant = ProductVariant.objects.filter(
            product_id=product_id,
            color_id=color_id or None,
            size_id=size_id or None,
            status='active'
        ).first()

        if variant:
            data = {
                'variant_price': float(variant.variant_price),
                'available_stock': variant.available_stock,
                'image_url': variant.image.url if variant.image else ''
            }
        else:
            data = {'variant_price': None, 'available_stock': 0, 'image_url': ''}

        return JsonResponse(data)



from django.shortcuts import render, get_object_or_404
from django.views import generic
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db.models import Avg, Q, Max, Min
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.template.loader import render_to_string
from account.mixing import LogoutRequiredMixin, LoginRequiredMixin
from store.models import (
    Category,
    Brand,
    Product,
    Slider,
    AcceptancePayment,
    ProductVariant,
    Review
)
import logging

logger = logging.getLogger('project')

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
         
        # ======= LOGGER =======
        logger.info(
            f"User {request.user if request.user.is_authenticated else 'Anonymous'} visited Home page. "
            f"Sliders: {sliders.count()}, "
            f"Feature Sliders: {feature_sliders.count()}, "
            f"Add Sliders: {add_sliders.count()}, "
            f"Promo Sliders: {promo_sliders.count()}, "
            f"Top Deals: {len(top_deals)}, "
            f"Featured Products: {featured_products.count()}"
        )
        context = {
            'sliders': sliders,
            'feature_sliders': feature_sliders,
            'add_sliders': add_sliders,
            'promo_sliders': promo_sliders,
            'acceptance_payments': acceptance_payments,
            'top_deals': top_deals,
            'first_top_deal': first_top_deal,
            'featured_products': featured_products,
        }

        return render(request, 'store/home.html', context)


# =========================================================
# PRODUCT DETAIL VIEW
# =========================================================
@method_decorator(never_cache, name='dispatch')
# class ProductDetailView(generic.View):
#     def get(self, request, slug, id):
#         # Fetch the main product with related data
#         product = get_object_or_404(
#             Product.objects.select_related('category', 'brand')
#                 .prefetch_related('reviews', 'variants__color', 'variants__size', 'images')
#                 .annotate(avg_rate=Avg('reviews__rating', filter=Q(reviews__status='active'))),
#             slug=slug,
#             id=id,
#             status='active'
#         )

#         # Fetch default variant (fallback to first if none)
#         default_variants = product.variants.filter(is_default=True)

#         if default_variants.exists():
#             variant = default_variants[0] 
#         else:
#             all_variants = product.variants.all()
#             if all_variants.exists():
#                 variant = all_variants[0]  
#             else:
#                 variant = None  

#         # Fetch related products (same category, exclude current)
#         related_products = Product.objects.filter(
#             category=product.category,
#             status='active'
#         ).exclude(id=product.id).select_related('category', 'brand') \
#          .prefetch_related('reviews').annotate(avg_rate=Avg('reviews__rating', filter=Q(reviews__status='active')))[:4]
       
#         # ===== LOGGER =====
#         logger.info(
#             f"User {request.user if request.user.is_authenticated else 'Anonymous'} "
#             f"visited ProductDetail page. Product: {product.title} (ID: {product.id}), "
#             f"Variant: {variant.id if variant else 'None'}, "
#             f"Related Products: {related_products.count()}"
#         )
#         context = {
#             'product': product,
#             'variant': variant,
#             'related_products': related_products
#         }

#         return render(request, 'store/product-detail.html', context)

class ProductDetailView(generic.View):
    def get(self, request, slug, id):
        product = get_object_or_404(
            Product.objects.select_related('category', 'brand')
                .prefetch_related('reviews', 'variants__color', 'variants__size', 'images')
                .annotate(avg_rate=Avg('reviews__rating', filter=Q(reviews__status='active'))),
            slug=slug,
            id=id,
            status='active'
        )


        default_variants = product.variants.filter(is_default=True)

        if default_variants.exists():
            variant = default_variants[0]
        else:
            all_variants = product.variants.all()
            if all_variants.exists():
                variant = all_variants[0]
            else:
                variant = None

 
        colors_qs = product.variants.filter(color__isnull=False).values("color__id", "color__title").distinct()
        sizes_qs = product.variants.filter(size__isnull=False).values("size__id", "size__title").distinct()

        colors = [{"id": x["color__id"], "title": x["color__title"]} for x in colors_qs]
        sizes = [{"id": x["size__id"], "title": x["size__title"]} for x in sizes_qs]

       
        related_products = Product.objects.filter(
            category=product.category,
            status='active'
        ).exclude(id=product.id).select_related('category', 'brand') \
         .prefetch_related('reviews').annotate(avg_rate=Avg('reviews__rating', filter=Q(reviews__status='active')))[:4]


        logger.info(
            f"User {request.user if request.user.is_authenticated else 'Anonymous'} "
            f"visited ProductDetail page. Product: {product.title} (ID: {product.id}), "
            f"Variant: {variant.id if variant else 'None'}, "
            f"Related Products: {related_products.count()}"
        )

        context = {
            'product': product,
            'variant': variant,
            'related_products': related_products,
            'colors': colors,   
            'sizes': sizes,     
        }

        return render(request, 'store/product-detail.html', context)


# =========================================================
# PRODUCT REVIEW VIEW (AJAX)
# =========================================================
@method_decorator(never_cache, name='dispatch')
class ProductReviewView(LoginRequiredMixin, generic.View):
    def post(self, request):
        user = request.user
        product_slug = request.POST.get('product_slug')
        product_id = request.POST.get('product_id')
        rating = request.POST.get('rating')
        subject = request.POST.get('subject')
        comment = request.POST.get('comment')

        if not rating or not rating.isdigit() or not subject or not comment:
            return JsonResponse({'status': 'error', 'message': 'All fields are required and rating must be a number'}, status=400)

        rating = float(rating)
        if rating < 1 or rating > 5:
            return JsonResponse({'status': 'error', 'message': 'Rating must be between 1 and 5'}, status=400)

        product = get_object_or_404(Product, slug=product_slug, id=product_id, status='active')

        # ---------- duplicate check ----------
        if Review.objects.filter(user=user, product=product).exists():
            return JsonResponse({'status': 'error', 'message': 'Already reviewed'}, status=400)

        review = Review.objects.create(
            user=user,
            product=product,
            rating=rating,
            subject=subject,
            comment=comment,
        )

        review_count = product.reviews.filter(status='active').count()

        # -------- SAFE profile image --------
        if hasattr(user, 'profile') and user.profile.image:
            image_url = user.profile.image.url
        else:
            image_url = '/media/defaults/default.jpg'

        review_html = f"""
        <div class="review-details-des">
            <div class="author-image mr-15">
                <img src="{image_url}" alt="{user.username}" style="width:50px;height:50px">
            </div>
            <div class="review-details-content">
                <h5>{review.rating:.2f}</h5>
                <div class="str-info">
                    <div class="review-star mr-15">
                        {"".join(
                            '<i class="text-warning fa fa-star"></i>' if i <= review.rating
                            else '<i class="text-warning fa fa-star-o"></i>'
                            for i in range(1, 6)
                        )}
                    </div>
                </div>
                <div class="name-date mb-30">
                    <h6>{user.username} –
                        <span>{review.created_date.strftime('%Y-%m-%d %H:%M')}</span>
                    </h6>
                </div>
                <p>{subject}</p>
                <p>{comment}</p>
            </div>
        </div>
        """

        logger.info(
            f"User {user.username} (ID: {user.id}) submitted a review for "
            f"Product: {product.title} (ID: {product.id}), "
            f"Rating: {rating}, Subject: {subject}"
        )

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
        per_page_options = [3, 6, 12]
        sort_options = ['latest', 'new', 'upcoming']

        products = (
            Product.objects
            .filter(status='active')
            .select_related('category', 'brand')
            .prefetch_related('reviews')
            .annotate(avg_rate=Avg('reviews__rating', filter=Q(reviews__status='active')))
        )
        banners = Slider.objects.filter(Q(slider_type='add') & Q(status='active'))[:1]

        # Pagination & Sorting
        per_page = request.GET.get('per_page')
        per_page = int(per_page) if per_page and per_page.isdigit() else 3

        sort_by = request.GET.get('sort', 'latest')

        page_number = request.GET.get('page')
        page_number = int(page_number) if page_number and page_number.isdigit() else 1

        sort_map = {
            'latest': '-created_date',
            'new': 'created_date',
            'upcoming': 'deadline'
        }

        if sort_by == 'upcoming':
            products = products.filter(deadline__gt=timezone.now()).order_by('deadline')
        else:
            products = products.order_by(sort_map.get(sort_by, '-created_date'))

        paginator = Paginator(products, per_page)
        page_obj = paginator.get_page(page_number)
        
    

        # ===== LOGGER =====
        logger.info(
            f"ShopView accessed | "
            f"User: {request.user.username if request.user.is_authenticated else 'Anonymous'} | "
            f"Page: {page_obj.number}/{paginator.num_pages} | "
            f"Per page: {per_page} | "
            f"Sort: {sort_by} | "
            f"Total products: {paginator.count}"
            f"Banners: {banners.count}"
        )

        context = {
            'products': page_obj,
            'banners': banners,
            'page_obj': page_obj,
            'per_page_options': per_page_options,
            'sort_options': sort_options,
            'selected_per_page': per_page,
            'selected_sort': sort_by,
        }

        # AJAX response
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            logger.info("ShopView AJAX request detected")
            return JsonResponse({
                'html': render_to_string('store/grid.html', context, request=request),
                'pagination_html': render_to_string('store/pagination.html', context, request=request)
            })

        return render(request, 'store/shop.html', context)


# =========================================================
# AJAX: GET FILTERED PRODUCTS
# =========================================================
@method_decorator(never_cache, name='dispatch')
class GetFilterProductsView(generic.View):
    def post(self, request):
        products = (
            Product.objects
            .filter(status='active')
            .select_related('category', 'brand')
            .prefetch_related('reviews')
            .annotate(avg_rate=Avg('reviews__rating', filter=Q(reviews__status='active')))
        )

        # Category filter
        category_ids = request.POST.getlist('category[]')
        if category_ids:
            products = products.filter(category_id__in=category_ids)

        # Brand filter
        brand_ids = request.POST.getlist('brand[]')
        if brand_ids:
            products = products.filter(brand_id__in=brand_ids)

        # Price filter
        max_price = request.POST.get('maxPrice')
        if max_price:
            products = products.filter(sale_price__lte=max_price)


        # Render HTML
        html = render_to_string('store/grid.html', {'products': products}, request=request)

        return JsonResponse({'html': html})
    

# =========================================================
# AJAX: GET PRODUCT VARIANT PRICE / STOCK / IMAGE
# =========================================================



from django.shortcuts import render, get_object_or_404
from django.views import generic
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.utils import timezone
from django.db.models import Avg, Q
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.template.loader import render_to_string
from account.mixing import LogoutRequiredMixin, LoginRequiredMixin
from store.models import (
    Category,
    Brand,
    Product,
    Size,
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
        active_sliders = Slider.objects.filter(status='active')
        sliders = active_sliders.filter(Q(slider_type='slider') | Q(slider_type='feature'))
        feature_sliders = active_sliders.filter(slider_type='feature')[:4]
        add_sliders = active_sliders.filter(slider_type='add')[:2]
        promo_sliders = active_sliders.filter(slider_type='promotion')[:3]
        acceptance_payments = AcceptancePayment.objects.filter(status='active')[:4]

        top_deals = list(
            Product.objects.filter(
                status='active',
                discount_percent__gt=0,
                is_deadline=True,
                deadline__gte=timezone.now(),
                available_stock__gt=0
            ).select_related('category', 'brand')
             .prefetch_related('reviews')
             .annotate(avg_rate=Avg('reviews__rating', filter=Q(reviews__status='active')))
             .order_by('-discount_percent', 'deadline')[:6]
        )
        first_top_deal = top_deals[0] if top_deals else None

        featured_products = Product.objects.filter(
            status='active',
            is_featured=True,
            available_stock__gt=0
        ).select_related('category', 'brand').prefetch_related('reviews') \
         .annotate(avg_rate=Avg('reviews__rating', filter=Q(reviews__status='active')))[:5]

        logger.info(
            "Home page visited",
            extra={
                "user": request.user.username if request.user.is_authenticated else "Anonymous",
                "sliders": sliders.count(),
                "feature_sliders": feature_sliders.count(),
                "add_sliders": add_sliders.count(),
                "promo_sliders": promo_sliders.count(),
                "top_deals": len(top_deals),
                "featured_products": featured_products.count(),
            }
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
class ProductDetailView(generic.View):
    def get(self, request, slug, id):
        product = get_object_or_404(
            Product.objects.select_related('category', 'brand')
            .prefetch_related('images', 'reviews', 'variants__color', 'variants__size')
            .annotate(avg_rate=Avg('reviews__rating', filter=Q(reviews__status='active'))),
            slug=slug,
            id=id,
            status='active',
            available_stock__gt=0
        )

        related_products = Product.objects.select_related('brand').prefetch_related('images').filter(
            category=product.category,
            status='active',
            available_stock__gt=0
        ).exclude(id=product.id)[:4]

        context = {'product': product, 'related_products': related_products}

        if product.variant != "None":
            variants = ProductVariant.objects.filter(
                product_id=id,
                status='active',
                available_stock__gt=0
            ).select_related('size', 'color').order_by('id')

            if variants.exists():
                default_variant = variants[0]
                sizes, used = [], set()
                for v in variants:
                    if v.size and v.size.id not in used:
                        sizes.append(v.size)
                        used.add(v.size.id)
                colors = [v for v in variants if v.size and v.size.id == default_variant.size.id]

                context.update({
                    'sizes': sizes,
                    'colors': colors,
                    'variant': default_variant,
                })
            else:
                context.update({'sizes': [], 'colors': [], 'variant': None})

        logger.info(
            "Product detail viewed",
            extra={
                "user": request.user.username if request.user.is_authenticated else "Anonymous",
                "product_id": product.id,
                "product_title": product.title,
                "variant_type": product.variant,
            }
        )
        return render(request, 'store/product-detail.html', context)


# =========================================================
# AJAX: GET VARIANT BY SIZE
# =========================================================
@method_decorator(never_cache, name='dispatch')
class GetVariantBySizeView(generic.View):
    def post(self, request):
        product_id = request.POST.get('product_id')
        size_id = request.POST.get('size_id')

        variants = ProductVariant.objects.filter(
            product_id=product_id,
            size_id=size_id,
            status='active',
            available_stock__gt=0
        ).select_related('size', 'color')

        variant = variants.first()  # first available

        html = render_to_string('store/color_options.html', {'colors': variants, 'variant': variant}, request=request)

        logger.info(
            "GetVariantBySize AJAX",
            extra={
                "product_id": product_id,
                "size_id": size_id,
                "variant_id": variant.id if variant else None
            }
        )

        return JsonResponse({
            'rendered_colors': html,
            'variant_id': variant.id if variant else None,
            'variant_price': str(variant.variant_price) if variant else '0',
            'variant_image': variant.image_url if variant and variant.image_url else '',
            'available_stock': variant.available_stock if variant else 0,
            'size': variant.size.code if variant and variant.size else '',
            'color': variant.color.title if variant and variant.color else '',
            'sku': variant.sku if variant and variant.sku else '',
            'title': variant.title if variant and variant.title else '',
        })


# =========================================================
# AJAX: GET VARIANT BY COLOR
# =========================================================
@method_decorator(never_cache, name='dispatch')
class GetVariantByColorView(generic.View):
    def post(self, request):
        variant_id = request.POST.get('variant_id')

        variant = get_object_or_404(
            ProductVariant.objects.select_related('size', 'color'),
            id=variant_id,
            status='active',
            available_stock__gt=0
        )

        logger.info(
            "GetVariantByColor AJAX",
            extra={
                "variant_id": variant.id,
                "product_id": variant.product.id
            }
        )

        return JsonResponse({
            'variant_id': variant.id,
            'variant_price': str(variant.variant_price),
            'available_stock': variant.available_stock,
            'variant_image': variant.image_url,
            'size': variant.size.code if variant.size else '',
            'color': variant.color.title if variant.color else '',
            'sku': variant.sku if variant.sku else '',
            'title': variant.title if variant.title else '',
        })


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
            return JsonResponse({'status': 'error', 'message': 'All fields required and rating must be a number'}, status=400)

        rating = float(rating)
        if rating < 1 or rating > 5:
            return JsonResponse({'status': 'error', 'message': 'Rating must be between 1 and 5'}, status=400)

        product = get_object_or_404(Product, slug=product_slug, id=product_id, status='active', available_stock__gt=0)

        if Review.objects.filter(user=user, product=product).exists():
            return JsonResponse({'status': 'error', 'message': 'Already reviewed'}, status=400)

        review = Review.objects.create(user=user, product=product, rating=rating, subject=subject, comment=comment)
        review_count = product.reviews.filter(status='active').count()
        image_url = user.image.url if hasattr(user, 'image') and user.image else '/media/defaults/default.jpg'

        review_html = f"""
        <div class="review-details-des">
            <div class="author-image mr-15">
                <img src="{image_url}" alt="{user.username}" style="width:50px;height:50px">
            </div>
            <div class="review-details-content">
                <h5>{review.rating:.2f}</h5>
                <div class="str-info">
                    <div class="review-star mr-15">
                        {"".join('<i class="text-warning fa fa-star"></i>' if i <= review.rating else '<i class="text-warning fa fa-star-o"></i>' for i in range(1,6))}
                    </div>
                </div>
                <div class="name-date mb-30">
                    <h6>{user.username} – <span>{review.created_at.strftime('%Y-%m-%d %H:%M')}</span></h6>
                </div>
                <p>{subject}</p>
                <p>{comment}</p>
            </div>
        </div>
        """

        logger.info(
            "Product review submitted",
            extra={
                "user_id": user.id,
                "username": user.username,
                "product_id": product.id,
                "product_title": product.title,
                "rating": rating,
                "subject": subject
            }
        )

        return JsonResponse({'status': 'success', 'message': 'Review submitted successfully', 'review_count': review_count, 'review_html': review_html})


# =========================================================
# SHOP VIEW WITH PAGINATION
# =========================================================
@method_decorator(never_cache, name='dispatch')
class ShopView(generic.View):
    def get(self, request):
        per_page_options = [3,6,12]
        sort_options = ['latest','new','upcoming']

        products = Product.objects.filter(status='active', available_stock__gt=0) \
            .select_related('category','brand') \
            .prefetch_related('reviews') \
            .annotate(avg_rate=Avg('reviews__rating', filter=Q(reviews__status='active')))

        banners = Slider.objects.filter(slider_type='add', status='active')[:1]

        per_page = int(request.GET.get('per_page') or 3)
        sort_by = request.GET.get('sort','latest')
        page_number = int(request.GET.get('page') or 1)

        sort_map = {'latest':'-created_at','new':'created_at','upcoming':'deadline'}
        if sort_by == 'upcoming':
            products = products.filter(deadline__gt=timezone.now()).order_by('deadline')
        else:
            products = products.order_by(sort_map.get(sort_by,'-created_at'))

        paginator = Paginator(products, per_page)
        page_obj = paginator.get_page(page_number)

        logger.info(
            "ShopView accessed",
            extra={
                "user": request.user.username if request.user.is_authenticated else "Anonymous",
                "page": page_obj.number,
                "total_pages": paginator.num_pages,
                "per_page": per_page,
                "sort": sort_by,
                "total_products": paginator.count,
                "banners_count": banners.count()
            }
        )

        context = {'products': page_obj,'banners': banners,'page_obj': page_obj,'per_page_options': per_page_options,'sort_options': sort_options,'selected_per_page': per_page,'selected_sort': sort_by}

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            logger.info("ShopView AJAX request detected")
            return JsonResponse({'html': render_to_string('store/grid.html',context,request=request),'pagination_html': render_to_string('store/pagination.html',context,request=request)})

        return render(request,'store/shop.html',context)


# =========================================================
# AJAX: GET FILTERED PRODUCTS
# =========================================================
@method_decorator(never_cache, name='dispatch')
class GetFilterProductsView(generic.View):
    def post(self, request):
        products = Product.objects.filter(status='active', available_stock__gt=0) \
            .select_related('category','brand') \
            .prefetch_related('reviews') \
            .annotate(avg_rate=Avg('reviews__rating', filter=Q(reviews__status='active')))

        category_ids = request.POST.getlist('category[]')
        if category_ids: products = products.filter(category_id__in=category_ids)

        brand_ids = request.POST.getlist('brand[]')
        if brand_ids: products = products.filter(brand_id__in=brand_ids)

        max_price = request.POST.get('maxPrice')
        if max_price: products = products.filter(sale_price__lte=max_price)

        html = render_to_string('store/grid.html', {'products': products}, request=request)

        logger.info(
            "Filtered products AJAX",
            extra={
                "category_ids": category_ids,
                "brand_ids": brand_ids,
                "max_price": max_price,
                "result_count": products.count()
            }
        )

        return JsonResponse({'html': html})

from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from store.views import(
    HomeView,
    ProductDetailView,
    ProductReviewView,
    ShopView,
    GetFilterProductsView,
)
urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('product-detail/<str:slug>/<int:id>/', ProductDetailView.as_view(), name='product-detail'),
    path('product-review/', ProductReviewView.as_view(), name='product-review'),
    path('shop/', ShopView.as_view(), name='shop'),
    path('get-filter-products/', csrf_exempt(GetFilterProductsView.as_view()), name='get-filter-products'),
]

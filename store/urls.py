from django.urls import path
from store.views import(
    HomeView,
    ProductDetailView,
    ShopView,
)
urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('product-detail', ProductDetailView.as_view(), name='product-detail'),
    path('shop/', ShopView.as_view(), name='shop'),
]

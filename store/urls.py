from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from store.views import(
    HomeView,
    ProductDetailView,
    ShopView,
    GetVariantsView,
)
urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('product-detail/<str:slug>/<int:id>/', ProductDetailView.as_view(), name='product-detail'),
    path('shop/', ShopView.as_view(), name='shop'),
    path('get-variants/', csrf_exempt(GetVariantsView.as_view()), name='get-variants'),
]

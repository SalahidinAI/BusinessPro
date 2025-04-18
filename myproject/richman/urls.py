from django.urls import path, include
from .views import *
from rest_framework import routers
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView

router = routers.SimpleRouter()

urlpatterns = [
    path('', include(router.urls)),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),

    path('password_reset/verify_code/', verify_reset_code, name='verify_reset_code'),
    path('password_reset/', include('django_rest_passwordreset.urls', namespace='password_reset')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('user/', UserProfileListAPIView.as_view(), name='user_list'),
    path('user/<int:pk>/', UserProfileEditAPIView.as_view(), name='user_detail'),

    # sellers
    path('seller/', SellerListAPIView.as_view(), name='seller_list'),
    path('seller/create/', SellerCreateAPIView.as_view(), name='seller_create'),
    path('seller/<int:pk>/', SellerEditAPIView.as_view(), name='seller_edit'),

    # groups
    path('group/', GroupListAPIView.as_view(), name='group_list'),
    path('group/create/', GroupCreateAPIView.as_view(), name='group_create'),
    path('group/<int:pk>/', GroupDetailAPIView.as_view(), name='group_detail'),

    # products
    path('group/<int:group_id>/product/create/', ProductCreateAPIView.as_view(), name='product_create'),
    path('product/<int:pk>/', ProductDetailAPIView.as_view(), name='product_edit'),

    # sizes
    path('product/<int:product_id>/size/create/', ProductSizeCreateAPIView.as_view(), name='product_size_create'),
    path('size/<int:pk>/', ProductSizeEditAPIView.as_view(), name='product_size_edit'),

    path('history/', HistoryAPIView.as_view(), name='history_list'),
]

from django.urls import path, include
from .views import *
from rest_framework import routers


router = routers.SimpleRouter()

urlpatterns = [
    path('', include(router.urls)),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),

    path('password_reset/verify_code/', verify_reset_code, name='verify_reset_code'),
    path('password_reset/', include('django_rest_passwordreset.urls', namespace='password_reset')),

    path('user/', UserProfileListAPIView.as_view(), name='user_list'),
    path('user/<int:pk>/', UserProfileEditAPIView.as_view(), name='user_detail'),

    path('group/', GroupListAPIView.as_view(), name='group_list'),
    path('group/create/', GroupCreateAPIView.as_view(), name='group_create'),
    path('group/<int:pk>/', GroupDetailAPIView.as_view(), name='group_detail'),

    path('seller/', SellerListAPIView.as_view(), name='seller_list'),
    path('seller/create/', SellerCreateAPIView.as_view(), name='seller_create'),
    path('seller/<int:pk>/', SellerEditAPIView.as_view(), name='seller_edit'),

    path('product/create/', ProductCreateAPIView.as_view(), name='product_create'),
    path('product/<int:pk>/', ProductDetailAPIView.as_view(), name='product_edit'),

    path('product_size/create/', ProductSizeCreateAPIView.as_view(), name='product_size_create'),
    path('product_size/<int:pk>/', ProductSizeEditAPIView.as_view(), name='product_size_edit'),

    path('history/', HistoryAPIView.as_view(), name='history_list'),
]

from django.urls import path, include
from .views import *
from rest_framework import routers


router = routers.SimpleRouter()
router.register(r'group', GroupViewSet, basename='group_list')


urlpatterns = [
    path('', include(router.urls)),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),

    path('users/', UserProfileListAPIView.as_view(), name='user_list'),

    path('users/<int:pk>/', UserProfileEditAPIView.as_view(), name='user_detail'),

    path('product/<int:pk>/', ProductDetailAPIView.as_view(), name='product_detail'),

    path('history/', SalesHistoryAPIView.as_view(), name='history'),
]

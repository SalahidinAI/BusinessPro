from django.db.models import Exists, OuterRef
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .serializers import *
from rest_framework import viewsets, generics
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import status
from .filters import SalesHistoryFilter
from rest_framework_simplejwt.tokens import RefreshToken


def refresh_access_token(request):
    refresh_token = request.data.get('refresh')  # Получаем refresh token из запроса
    try:
        refresh = RefreshToken(refresh_token)
        access_token = refresh.access_token  # Новый access token
        # Возвращаем оба токена
        return Response({
            'access': str(access_token),
            'refresh': str(refresh),  # Новый refresh token
        })
    except Exception as e:
        return Response({'detail': str(e)}, status=400)


class RegisterView(generics.CreateAPIView):
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CustomLoginView(TokenObtainPairView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception:
            return Response({"detail": "Неверные учетные данные"}, status=status.HTTP_401_UNAUTHORIZED)

        user = serializer.validated_data
        return Response(serializer.data, status=status.HTTP_200_OK)


class LogoutView(generics.GenericAPIView):
    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class UserProfileListAPIView(generics.ListAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileListSerializer


class UserProfileEditAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileDetailSerializer

    def get_queryset(self):
        return UserProfile.objects.filter(password=self.request.user.password)


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['products__sizes__size', 'products__sizes__have']
    search_fields = ['products__product_name']
    ordering_fields = ['group_name', 'created_date']

    def get_serializer_class(self):
        if self.action == 'list':
            return GroupListSerializer
        return GroupDetailSerializer

    def get_queryset(self):
        size_filter = self.request.query_params.get('products__sizes__size')
        if self.request.user.is_authenticated:
            queryset = Group.objects.filter(owner=self.request.user)
        else:
            queryset = Group.objects.none()

        if size_filter:
            queryset = queryset.filter(
                Exists(
                    ProductSize.objects.filter(
                        size=size_filter,
                        have=True,
                        product__group=OuterRef('pk')
                    )
                )
            )
        return queryset.distinct()


class GroupDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Group.objects.all().distinct()
    serializer_class = GroupDetailSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['products__sizes__size', ]
    search_fields = ['products__product_name']
    ordering_fields = ['group_name', 'created_date']

    def get_queryset(self):
        return Group.objects.filter(owner=self.request.user)


class ProductDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductDetailSerializer

    def get_queryset(self):
        return Product.objects.filter(group__owner=self.request.user)


class SalesHistoryAPIView(generics.ListAPIView):
    queryset = SalesHistory.objects.all()
    serializer_class = SalesHistorySerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = SalesHistoryFilter

    def get_queryset(self):
        return SalesHistory.objects.filter(owner=self.request.user)

from django.db.models import Exists, OuterRef
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .serializers import *
from rest_framework import generics, status
from rest_framework_simplejwt.views import TokenObtainPairView
from .filters import *
from rest_framework_simplejwt.tokens import RefreshToken
from .permissions import *
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import VerifyResetCodeSerializer


@api_view(['POST'])
def verify_reset_code(request):
    serializer = VerifyResetCodeSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'Пароль успешно сброшен.'}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegisterView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

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
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return UserProfile.objects.filter(id=self.request.user.id)


class UserProfileEditAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileEditSerializer
    permission_classes = [CheckUserEdit]


class GroupListAPIView(generics.ListAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupListSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['products__sizes__size', 'products__sizes__have']
    search_fields = ['products__product_name']
    ordering_fields = ['group_name', 'created_date']


    # здесь фильтр по размеру и проверяется have=True
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


class GroupDetailAPIView(generics.RetrieveAPIView):
    queryset = Group.objects.all().distinct()
    serializer_class = GroupDetailSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    permission_classes = [CheckEdit]
    filterset_fields = ['products__sizes__size', ]
    search_fields = ['products__product_name']
    ordering_fields = ['group_name', 'created_date']


class SellerListAPIView(generics.ListAPIView):
    queryset = Seller.objects.all()
    serializer_class = SellerNameSerializer

    def get_queryset(self):
        return Seller.objects.filter(owner=self.request.user)


class SellerCreateAPIView(generics.CreateAPIView):
    serializer_class = SellerSerializer


class SellerEditAPIView(generics.RetrieveUpdateAPIView):
    queryset = Seller.objects.all()
    serializer_class = SellerSerializer
    permission_classes = [CheckEdit]


class GroupCreateAPIView(generics.CreateAPIView):
    serializer_class = GroupSerializer


class ProductCreateAPIView(generics.CreateAPIView):
    serializer_class = ProductSerializer


class ProductDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductDetailSerializer
    permission_classes = [CheckProductEdit]


class ProductSizeCreateAPIView(generics.CreateAPIView):
    serializer_class = ProductSizeSerializer


class ProductSizeEditAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ProductSize.objects.all()
    serializer_class = ProductSizeSerializer
    permission_classes = [CheckProductSizeEdit]


class HistoryAPIView(generics.ListAPIView):
    queryset = History.objects.all()
    serializer_class = HistorySerializer
    # filter_backends = [DjangoFilterBackend, SearchFilter]
    # filterset_class = SalesHistoryFilter

    def get_queryset(self):
        return History.objects.filter(user=self.request.user)

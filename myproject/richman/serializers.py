from django_rest_passwordreset.models import ResetPasswordToken
from rest_framework import serializers
from .models import *
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate


class VerifyResetCodeSerializer(serializers.Serializer):
    email = serializers.EmailField()  # Email пользователя
    reset_code = serializers.IntegerField()  # 4-значный код
    new_password = serializers.CharField(write_only=True)  # Новый пароль

    def validate(self, data):
        email = data.get('email')
        reset_code = data.get('reset_code')

        # Проверяем, существует ли указанный код для email
        try:
            token = ResetPasswordToken.objects.get(user__email=email, key=reset_code)
        except ResetPasswordToken.DoesNotExist:
            raise serializers.ValidationError("Неверный код сброса или email.")

        data['user'] = token.user
        return data

    def save(self):
        user = self.validated_data['user']
        new_password = self.validated_data['new_password']

        # Устанавливаем новый пароль
        user.set_password(new_password)
        user.save()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('username', 'first_name', 'last_name',
                  'age', 'email', 'phone', 'password', 'date_registered')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = UserProfile.objects.create_user(**validated_data)
        return user

    def to_representation(self, instance):
        refresh = RefreshToken.for_user(instance)
        return {
            'user': {
                'username': instance.username,
                'email': instance.email,
            },
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Неверные учетные данные")


class UserProfileListSerializer(serializers.ModelSerializer):
    date_registered = serializers.DateTimeField(format='%d-%m-%Y %H:%M')

    class Meta:
        model = UserProfile
        fields = ['id', 'password', 'username', 'first_name', 'last_name',
                  'email', 'age', 'phone', 'date_registered']


class UserProfileEditSerializer(serializers.ModelSerializer):
    date_registered = serializers.DateTimeField(format='%d-%m-%Y %H:%M')

    class Meta:
        model = UserProfile
        fields = ['id', 'password', 'username', 'first_name', 'last_name',
                  'email', 'age', 'phone', 'date_registered']


class SellerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seller
        fields = ['seller_name']


class SellerNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seller
        fields = ['seller_name']


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['group_date']


class GroupListSerializer(serializers.ModelSerializer):
    group_date = serializers.DateField(format='%d %B %Y')
    owner = UserProfile()
    count_products = serializers.SerializerMethodField()
    count_sold_sizes = serializers.SerializerMethodField()
    count_all_sizes = serializers.SerializerMethodField()
    group_spend = serializers.SerializerMethodField()
    products_income = serializers.SerializerMethodField()
    products_profit = serializers.SerializerMethodField()

    class Meta:
        model = Group  # if u need, add 'created_date'
        fields = ['id', 'group_date', 'owner', 'count_products', 'count_sold_sizes', 'count_all_sizes',
                  'group_spend', 'products_income', 'products_profit']

    def get_count_products(self, obj):
        return obj.get_count_products()

    def get_count_sold_sizes(self, obj):
        return obj.get_count_sold_sizes()

    def get_count_all_sizes(self, obj):
        return obj.get_count_all_sizes()

    def get_group_spend(self, obj):
        return obj.get_group_spend()

    def get_products_income(self, obj):
        return obj.get_products_income()

    def get_products_profit(self, obj):
        return obj.get_products_profit()


class ProductSizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductSize
        fields = '__all__'


class ProductSizeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductSize
        fields = ['size']


class ProductSizeDetailSerializer(serializers.ModelSerializer):
    # sold_date = serializers.DateTimeField(format('%d-%m-%Y %H:%M'))
    get_profit = serializers.ModelSerializer()

    class Meta:
        model = ProductSize # if need add sold_date, now I dont need
        fields = ['size', 'have', 'high_price', 'get_profit']

    def get_profit(self, obj):
        return obj.get_profit()


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ограничиваем выбор групп только для владельца
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            self.fields['group'].queryset = Group.objects.filter(owner=request.user)


class ProductListSerializer(serializers.ModelSerializer):
    sizes = ProductSizeListSerializer(many=True, read_only=True)
    products_spend = serializers.SerializerMethodField()
    products_income = serializers.SerializerMethodField()
    products_profit = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'image', 'product_name', 'article', 'sizes', 'products_spend',
                  'products_income', 'products_profit'] # 'group', 'description', 'low_price', 'high_price', 'created_date',

    def get_products_spend(self, obj):
        return obj.get_products_spend()

    def get_products_income(self, obj):
        return obj.get_products_income()

    def get_products_profit(self, obj):
        return obj.get_products_profit()


class ProductNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['product_name', 'article', 'low_price']


class ProductSizeNamePriceSerializer(serializers.ModelSerializer):
    seller = SellerNameSerializer()

    class Meta:
        model = ProductSize
        fields = ['size', 'high_price', 'seller']


class HistoryItemSerializer(serializers.ModelSerializer):
    sold_date = serializers.DateTimeField(format='%d-%m-%Y %H:%M')
    product_size = ProductSizeNamePriceSerializer()
    product = ProductNameSerializer()

    class Meta:
        model = HistoryItem
        fields = ['product', 'product_size', 'sold_date']


class HistorySerializer(serializers.ModelSerializer):
    history_items = HistoryItemSerializer(many=True, read_only=True)

    class Meta:
        model = History
        fields = ['user', 'history_items']


class GroupDetailSerializer(serializers.ModelSerializer):
    group_date = serializers.DateField(format='%d-%m-%Y')
    products = ProductListSerializer(many=True, read_only=True)

    class Meta:
        model = Group
        fields = ['group_date', 'products']


class ProductDetailSerializer(serializers.ModelSerializer):
    created_date = serializers.DateTimeField(format='%d-%m-%Y %H:%M')
    sizes = ProductSizeDetailSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = ['image', 'product_name', 'article', 'description', 'low_price', 'sizes', 'created_date']

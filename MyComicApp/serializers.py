from rest_framework import serializers

from .models import Role, User,Product, Category

from .models import User

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Order, OrderItem
from decimal import Decimal
from django.utils import timezone

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'password', 'address','phone', 'image']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create(
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            email=validated_data['email'],
            address=validated_data['address'],
            phone=validated_data['phone'],
            image=validated_data.get('image')
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

    def update(self, instance, validated_data):
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.address = validated_data.get('address', instance.address)
        instance.phone = validated_data.get('phone', instance.phone)
        instance.image = validated_data.get('image', instance.image)

        password = validated_data.get('password', None)
        if password:
            instance.set_password(password)
        
        instance.save()
        return instance


class LogoutSerializer(serializers.Serializer):
    user = serializers.IntegerField()

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        return token

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'
        
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'



#Order Serializer---> Order Items Serializer 
class OrderItemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity']

 
class OrderCreateSerializer(serializers.ModelSerializer):
    order_items = OrderItemCreateSerializer(many=True)

    class Meta:
        model = Order
        fields = ['state', 'payment_method', 'shipping_method', 'payment_status', 'total_amount', 'order_items']

    def validate(self, attrs):
        order_items_data = attrs.get('order_items', [])
        for order_item_data in order_items_data:
            if 'product' not in order_item_data:
                raise serializers.ValidationError("Cada elemento de 'order_items' debe tener una clave 'product'.")
            product = order_item_data['product']
            quantity = order_item_data['quantity']
            if product.stock < quantity:
                raise serializers.ValidationError(f"No hay suficiente stock para {product.name}")
        attrs.setdefault('state', 'En proceso')
        attrs.setdefault('order_date', timezone.now().date())
        attrs.setdefault('payment_method', 'credit_card')
        attrs.setdefault('shipping_method', 'express')
        attrs.setdefault('payment_status', 'pagado')
        return attrs

    def create(self, validated_data):
        order_items_data = validated_data.pop('order_items')
        total_amount = Decimal(0)
        
        for order_item_data in order_items_data:
            product = order_item_data['product']
            quantity = order_item_data['quantity']
            subtotal = product.price * quantity
            total_amount += subtotal
            
            # Actualizar el stock del producto
            product.stock -= quantity
            product.save()
        
        validated_data['total_amount'] = total_amount
        order = Order.objects.create(**validated_data)
        
        for order_item_data in order_items_data:
            OrderItem.objects.create(order=order, **order_item_data)
        
        return order

class OrderItemSerializer(serializers.ModelSerializer):
    product = serializers.StringRelatedField()

    class Meta:
        model = OrderItem
        fields = ['id_order_items', 'product', 'quantity']

class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, read_only=True)
    user = serializers.StringRelatedField()

    class Meta:
        model = Order
        fields = ['id_order', 'user', 'state', 'order_date', 'payment_method', 'shipping_method', 'payment_status', 'total_amount', 'order_items']


from rest_framework import serializers
from .models import MenuItem, Category,  Cart, Order, OrderItem
from django.contrib.auth.models import User

class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ['id', 'title', 'price', 'featured', 'category']
        depth = 1

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['slug']

class ManagerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class CartHelperSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ['id', 'title', 'price']

class CartSerializer(serializers.ModelSerializer):
    menu_item = CartHelperSerializer()
    class Meta:
        model = Cart
        fields = ['menu_item', 'quantity', 'price']

class CartAddSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ['menu_item', 'quantity']
        extra_kwargs = {
            'quantity': {'min_value': 1}
        }

class CartRemoveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ['menu_item']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username']

class OrderSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    class Meta:
        model = Order
        fields = ['id', 'user', 'total', 'status', 'delivery_crew', 'date']

class SingleHelperSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ['title', 'price']

class SingleOrderSerializer(serializers.ModelSerializer):
    menu_item = SingleHelperSerializer()
    class Meta:
        model = OrderItem
        fields = ['menu_item', 'quantity']

class OrderPutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['delivery_crew']
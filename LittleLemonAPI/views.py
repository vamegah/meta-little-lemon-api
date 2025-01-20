
from rest_framework import generics
from django.http import HttpResponseBadRequest
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from .models import MenuItem, Category, Cart, Order, OrderItem
from .serializers import MenuItemSerializer, CategorySerializer, CartSerializer, OrderSerializer, ManagerSerializer, CartAddSerializer, CartRemoveSerializer, SingleOrderSerializer, OrderPutSerializer
from .pagination import MenuItemListPagination
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .permission import IsManager, IsDeliveryCrew
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User, Group
import math
import datetime



# Create your views here.
class MenuItemListView(generics.ListCreateAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    search_fields = ['title', 'category_title'] # search by title and category
    ordering_fields = ['price', 'category'] # order by title, price and category
    pagination_class = MenuItemListPagination

    def get_permissions(self):
        permission_classes = []
        if self.request.method !='GET':
            permission_classes = [IsAuthenticated, IsAdminUser]
        return [permission() for permission in permission_classes]
    
    

class CategoryListView(generics.ListCreateAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    permission_classes = [IsAdminUser]

class MenuItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

    def get_permissions(self):
        permission_classes = [IsAuthenticated]
        if self.request.method =='PATCH':
            permission_classes = [IsAuthenticated, IsManager | IsAdminUser]
        if self.request.method =='DELETE':
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]
    
    def patch(self, request, *args, **kwargs):
        menu_item = MenuItem.objects.get(pk=self.kwargs['pk'])
        menu_item.featured = not menu_item.featured
        menu_item.save()
        return JsonResponse(status=200, data={'message': 'Featured status of {} changed to {}'.format(str(menu_item.title), str(menu_item.featured))})
           
class ManagerListView(generics.ListCreateAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    permission_classes = [IsAuthenticated, IsManager |IsAdminUser]

    def post(self, request, *args, **kwargs):
        username = request.data['username']
        if username:
            user = get_object_or_404(User, username=username)
            manager = Group.objects.get(name='Manager')
            manager.user_set.add(user)
            return JsonResponse(status=201, data={'message': 'User added to Manager group'})
    

class ManagerRemoveView(generics.DestroyAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated, IsManager | IsAdminUser]
    queryset = User.objects.filter(groups__name='Manager')

    def delete(self, request, *args, **kwargs):
            pk = self.kwargs['pk']
            user = get_object_or_404(User, pk=pk)
            manager = Group.objects.get(name='Manager')
            manager.user_set.remove(user)
            return JsonResponse(status=200, data={'message': 'User removed from Manager group'})

class DeliveryCrewListView(generics.ListCreateAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    permission_classes = [IsAuthenticated, IsManager | IsAdminUser]

    def post(self, request, *args, **kwargs):
        username = request.data['username']
        if username:
            user = get_object_or_404(User, username=username)
            delivery_crew = Group.objects.get(name='Delivery Crew')
            delivery_crew.user_set.add(user)
            return JsonResponse(status=201, data={'message': 'User added to Delivery Crew group'})

class DeliveryCrewRemoveView(generics.DestroyAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    serializer_class = ManagerSerializer
    permission_classes = [IsAuthenticated, IsManager | IsAdminUser]
    queryset = User.objects.filter(groups__name='Delivery Crew')

    def delete(self, request, *args, **kwargs):
            pk = self.kwargs['pk']
            user = get_object_or_404(User, pk=pk)
            delivery_crew = Group.objects.get(name='Delivery Crew')
            delivery_crew.user_set.remove(user)
            return JsonResponse(status=200, data={'message': 'User removed from Delivery Crew group'})

class CartListView(generics.ListCreateAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self, *args, **kwargs):
        return Cart.objects.filter(user=self.request.user)

    def post(self, request, *args, **kwargs):
        serialized_item = CartAddSerializer(data=request.data)
        serialized_item.is_valid(raise_exception=True)
        id = request.data['menu_item']
        quantity = request.data['quantity']
        item = get_object_or_404(MenuItem, id=id)
        price = item.price*int(quantity)
        try:
            cart = Cart.objects.create(user=request.user, quantity=quantity, unit_price=item.price, price=price, menu_item_id=id)
        except:
            return JsonResponse(status=400, data={'message': 'Item already in cart'})
        return JsonResponse(status=201, data={'message': 'Item added to cart'})
    
    def delete(self, request, *args, **kwargs):
        if request.data['menu_item']:
            serialized_item = CartRemoveSerializer(data=request.data)
            serialized_item.is_valid(raise_exception=True)
            menu_item = request.data['menu_item']
            cart = get_object_or_404(Cart, user=request.user, menu_item=menu_item)
            cart.delete()
            return JsonResponse(status=200, data={'message': 'Item removed from cart'})
        else:
            Cart.objects.filter(user=request.user).delete()
            return JsonResponse(status=200, data={'message': 'Cart cleared'})
         

class OrderListView(generics.ListCreateAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    serializer_class = OrderSerializer

    def get_queryset(self, *args, **kwargs):
        if self.request.user.groups.filter(name='Manager').exists() or self.request.user.is_superuser == True:
            query = Order.objects.all()
        elif self.request.user.groups.filter(name='Delivery Crew').exists():
            query = Order.objects.filter(delivery_crew=self.request.user)
        else:
            query = Order.objects.filter(user=self.request.user)
        return query
    
    def get_permissions(self):
        
        if self.request.method == 'GET' or self.request.method == 'POST':
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthenticated, IsManager | IsAdminUser]
        return [permission() for permission in permission_classes]
       

    def post(self, request, *args, **kwargs):
        cart = Cart.objects.filter(user=request.user)
        x = cart.values_list()
        if len(x) == 0:
            return HttpResponseBadRequest()
        total = math.fsum([i[4] for i in x])
        order = Order.objects.create(user=request.user, total=total, status=False, date=datetime.date.today())
        for item in cart.values():
            menu_item = get_object_or_404(MenuItem, id=item['menu_item_id'])
            order_item = OrderItem.objects.create(order=order, menu_item=menu_item, quantity=item['quantity'])
            order_item.save()
        cart.delete()
        return JsonResponse(status=201, data={'message': 'Your order has been placed. Your order number is {}'.format(str(order.id))})
       

class SingleOrderView(generics.ListCreateAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    serializer_class = SingleOrderSerializer
    
    def get_permissions(self):
        order = Order.objects.get(pk=self.kwargs['pk'])
        if self.request.user == order.user and self.request.method == 'GET':
            permission_classes = [IsAuthenticated]
        elif self.request.method == 'PUT' or self.request.method == 'DELETE':
            permission_classes = [IsAuthenticated, IsManager | IsAdminUser]
        else:
            permission_classes = [IsAuthenticated, IsDeliveryCrew | IsManager | IsAdminUser]
        return [permission() for permission in permission_classes]

    def get_queryset(self, *args, **kwargs):
        return OrderItem.objects.filter(id=self.kwargs['pk'])

    def patch(self, request, *args, **kwargs):
        serialized_item = OrderPutSerializer(data=request.data)
        serialized_item.is_valid(raise_exception=True)
        order_pk = self.kwargs['pk']
        crew_pk = request.data['delivery_crew']
        order = get_object_or_404(Order, pk=order_pk)
        crew = get_object_or_404(User, pk=crew_pk)
        order.delivery_crew = crew
        order.save()
        return JsonResponse(status=200, data={'message': 'Delivery crew assigned to order'})
    
    def delete(self, request, *args, **kwargs):
        order = Order.objects.get(pk=self.kwargs['pk'])
        order_number = str(order.id)
        order.delete()
        return JsonResponse(status=200, data={'message': 'Order #{} was deleted' .format(order_number)})
    




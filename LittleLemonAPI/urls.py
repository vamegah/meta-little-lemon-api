
from django.urls import path, include
from . import views

urlpatterns = [
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('menu-items', views.MenuItemListView.as_view(), name='menu-list'),
    path('menu-items/<int:pk>', views.MenuItemDetailView.as_view(), name='menu-detail'),
    path('category/', views.CategoryListView.as_view(), name='category-list'),
    path('groups/manager/users', views.ManagerListView.as_view(), name='manager-list'),
    path('groups/manager/users/<int:pk>', views.ManagerRemoveView.as_view(), name='manager-remove'),
    path('groups/delivery-crew/users', views.DeliveryCrewListView.as_view(), name='delivery-crew-list'),
    path('groups/delivery-crew/users/<int:pk>', views.DeliveryCrewRemoveView.as_view(), name='delivery-crew-remove'),
    path('cart/menu-items', views.CartListView.as_view(), name='cart-list'),
    path('order', views.OrderListView.as_view(), name='order-list'),
    path('order/<int:pk>', views.SingleOrderView.as_view(), name='single-order'),
    
]
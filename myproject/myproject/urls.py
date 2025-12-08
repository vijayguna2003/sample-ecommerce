from django.contrib import admin
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('products/', views.product_list, name='products'),
    path('contact/', views.contact, name='contact'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('register/', views.register_user, name='register'),

    path('cart/', views.view_cart, name='cart'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<int:cart_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),

    path('my-orders/', views.myorder, name='my_order'),
    path('order/<int:order_id>/', views.orderdetail, name='orderdetail'),

    # 👉 ADD THIS LINE (Register URL)
    path('register/', views.register_user, name='register'),

    path('profile/', views.profile_dashboard, name='profile_dashboard'),
    path('profile/edit/', views.edit_profile, name='editprofile'),
    path('profile/change-password/', views.change_password, name='change_password'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.db.models import Sum

from .models import Product, Cart, CartItem, Order, OrderItem, UserProfile
from .forms import UserUpdateForm, ProfileUpdateForm

# Public pages
def home(request):
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')

def product_list(request):
    products = Product.objects.all()
    return render(request, 'products.html', {'products': products})
def login_user(request):
    return render(request, 'home.html')

# Auth (simple)
def register_user(request):   
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email', '')
        from django.contrib.auth.models import User
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return redirect('register')
        User.objects.create_user(username=username, password=password, email=email)
        messages.success(request, 'User created. Please login.')
        return redirect('login')
    return render(request, 'register.html')

def login_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('home')
        messages.error(request, 'Invalid credentials')
    return render(request, 'login.html')

def logout_user(request):
    logout(request)
    return redirect('home')

# CART
@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    cart_item, created = CartItem.objects.get_or_create(
        user=request.user,
        product=product
    )
    if not created:
        cart_item.quantity += 1
        cart_item.save()

    messages.success(request, "Product added to cart!")
    return redirect("cart")


@login_required
def view_cart(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total = sum(item.total_price() for item in cart_items)
    return render(request, 'cart.html', {'cart_items': cart_items, 'total': total})

@login_required
def remove_from_cart(request, cart_id):
    item = get_object_or_404(CartItem, id=cart_id, user=request.user)
    item.delete()
    messages.success(request, "Item removed from your cart.")
    return redirect('cart')

# CHECKOUT (offline / dummy)
@login_required
def checkout(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total = sum(item.total_price() for item in cart_items)
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        order = Order.objects.create(
            user=request.user,
            total_amount=total,
            payment_method=payment_method,
            payment_status='Completed' if payment_method == 'PAID' else 'Pending'
        )
        for item in cart_items:
            OrderItem.objects.create(order=order, product=item.product, quantity=item.quantity, price=item.product.price)
        cart_items.delete()
        messages.success(request, f"Order #{order.id} placed successfully!")
        return redirect('my_order')
    return render(request, 'checkout.html', {'cart_items': cart_items, 'total': total})

# ORDERS
@login_required
def myorder(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'my_order.html', {'orders': orders})

@login_required
def orderdetail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    items = order.items.all()
    return render(request, 'orderdetail.html', {'order': order, 'items': items})

# PROFILE
@login_required
def profile_dashboard(request):
    user = request.user
    orders = Order.objects.filter(user=user)
    total_orders = orders.count()
    total_spent = orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    recent_items = OrderItem.objects.filter(order__user=user).order_by('-order__created_at')[:5]
    return render(request, 'profile_dashboard.html', {
        'user': user,
        'total_orders': total_orders,
        'total_spent': total_spent,
        'recent_items': recent_items,
    })

@login_required
@login_required
def edit_profile(request):
    user = request.user

    profile, created = UserProfile.objects.get_or_create(user=user)

    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('profile_dashboard')

    else:
        u_form = UserUpdateForm(instance=user)
        p_form = ProfileUpdateForm(instance=profile)

    return render(request, 'editprofile.html', {'u_form': u_form, 'p_form': p_form})

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Password updated successfully!')
            return redirect('profile_dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'change_password.html', {'form': form})
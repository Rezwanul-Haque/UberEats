from django.db.models import Sum, Count, Case, When
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User

from datetime import datetime, timedelta

from foodtaskerapp.forms import UserForm, RestaurantForm, UserFormForEdit, MealForm
from foodtaskerapp.models import Meal, Order, Driver
# Create your views here.


def home(request):
    return redirect(restaurant_home)


@login_required(login_url='/restaurant/sign-in/')
def restaurant_home(request):
    return redirect(restaurant_order)


@login_required(login_url='/restaurant/sign-in/')
def restaurant_account(request):
    user_form = UserFormForEdit(instance=request.user)
    restaurant_form = RestaurantForm(instance=request.user.restaurant)

    if request.method == "POST":
        user_form = UserFormForEdit(request.POST, instance=request.user)
        restaurant_form = RestaurantForm(request.POST, request.FILES, instance=request.user.restaurant)

        if user_form.is_valid() and restaurant_form.is_valid():
            user_form.save()
            restaurant_form.save()

    context = {
        'user_form': user_form,
        'restaurant_form': restaurant_form
    }
    return render(request, "restaurant/account.html", context)


@login_required(login_url='/restaurant/sign-in/')
def restaurant_meal(request):
    meals = Meal.objects.filter(restaurant=request.user.restaurant).order_by('-id')
    context = {
        'meals': meals
    }
    return render(request, "restaurant/meal.html", context)


@login_required(login_url='/restaurant/sign-in/')
def restaurant_add_meal(request):
    meal_form = MealForm()

    if request.method == "POST":
        meal_form = MealForm(request.POST, request.FILES)

        if meal_form.is_valid():
            meal = meal_form.save(commit=False)
            meal.restaurant = request.user.restaurant
            meal.save()
            return redirect(restaurant_meal)
    context = {
        'meal_form': meal_form
    }
    return render(request, "restaurant/add_meal.html", context)


@login_required(login_url='/restaurant/sign-in/')
def restaurant_edit_meal(request, meal_id):
    meal_form = MealForm(instance=Meal.objects.get(id=meal_id))

    if request.method == "POST":
        meal_form = MealForm(request.POST, request.FILES, instance=Meal.objects.get(id=meal_id))

        if meal_form.is_valid():
            meal_form.save()
            return redirect(restaurant_meal)
    context = {
        'meal_form': meal_form
    }
    return render(request, "restaurant/edit_meal.html", context)


@login_required(login_url='/restaurant/sign-in/')
def restaurant_order(request):
    if request.method == "POST":
        order = Order.objects.get(id=request.POST['id'], restaurant=request.user.restaurant)

        if order.status == Order.COOKING:
            order.status = Order.READY
            order.save()
    orders = Order.objects.filter(restaurant=request.user.restaurant).order_by('-id')
    context = {
        'orders': orders,
    }
    return render(request, "restaurant/order.html", context)


@login_required(login_url='/restaurant/sign-in/')
def restaurant_report(request):
    # Calculate revenue and number of order by current week
    revenue = []
    orders = []

    # Calculate weekdays
    today = datetime.now()
    current_weekdays = [today + timedelta(days=i) for i in range(0 - today.weekday(), 7 - today.weekday())]
    for day in current_weekdays:
        delivered_orders = Order.objects.filter(
            restaurant=request.user.restaurant,
            status=Order.DELIVERED,
            created_at__year=day.year,
            created_at__month=day.month,
            created_at__day=day.day
        )
        revenue.append(sum(order.total for order in delivered_orders))
        orders.append(delivered_orders.count())

    # Top 3 Meals
    top3_meals = Meal.objects.filter(restaurant=request.user.restaurant,
                                     ).annotate(total_order=Sum("orderdetails__quantity"))\
                                      .order_by("-total_order")[:3]

    meal = {
        "labels": [meal.name for meal in top3_meals],
        "data": [meal.total_order or 0 for meal in top3_meals]
    }

    # Top 3 Drivers
    top3_drivers = Driver.objects.annotate(
        total_order=Count(
            Case(
                When(order__restaurant=request.user.restaurant,
                     then=1)
            )
        )
    ).order_by("-total_order")[:3]

    driver = {
        "labels": [driver.user.get_full_name() for driver in top3_drivers],
        "data": [driver.total_order for driver in top3_drivers]
    }

    context = {
        "revenue": revenue,
        "orders": orders,
        "meal": meal,
        "driver": driver
    }

    return render(request, "restaurant/report.html", context)


def restaurant_sign_up(request):
    user_form = UserForm()
    restaurant_form = RestaurantForm()

    if request.method == 'POST':
        user_form = UserForm(request.POST)
        restaurant_form = RestaurantForm(request.POST, request.FILES)

        if user_form.is_valid() and restaurant_form.is_valid():
            new_user = User.objects.create_user(**user_form.cleaned_data)
            new_restaurant = restaurant_form.save(commit=False)
            new_restaurant.user = new_user
            new_restaurant.save()

            login(request, authenticate(
                username=user_form.cleaned_data["username"],
                password=user_form.cleaned_data["password"]
            ))

            return redirect(restaurant_home)
    context = {
        "user_form": user_form,
        "restaurant_form": restaurant_form
    }
    return render(request, "restaurant/sign_up.html", context)
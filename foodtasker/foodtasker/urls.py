"""foodtasker URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
from django.conf import settings

from foodtaskerapp import views, apis


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r"^$", views.home, name="home"),

    # Restaurant
    url(r'^restaurant/sign-in/$', auth_views.login,
        {'template_name': 'restaurant/sign_in.html'},
        name="restaurant-sign-in"),
    url(r'^restaurant/sign-out/$', auth_views.logout,
        {'next_page': '/'},
        name="restaurant-sign-out"),
    url(r'^restaurant/sign-up/$', views.restaurant_sign_up,
        name="restaurant-sign-up"),
    url(r'^restaurant/$', views.restaurant_home, name="restaurant-home"),

    url(r'^restaurant/account/$', views.restaurant_account, name="restaurant-account"),
    url(r'^restaurant/meal/$', views.restaurant_meal, name="restaurant-meal"),
    url(r'^restaurant/meal/add/$', views.restaurant_add_meal, name="restaurant-add-meal"),
    url(r'^restaurant/meal/edit/(?P<meal_id>\d+)/$', views.restaurant_edit_meal, name="restaurant-edit-meal"),
    url(r'^restaurant/order/$', views.restaurant_order, name="restaurant-order"),
    url(r'^restaurant/report/$', views.restaurant_report, name="restaurant-report"),


    # Sign up / Sign In by social media
    url(r'^api/social/', include('rest_framework_social_oauth2.urls')),
    # /convert-token (sign-in / sign-up)
    # /revoke-token (sign-out)

    url(r'^api/restaurant/order/notification/(?P<last_request_time>.+)/$', apis.restaurant_order_notification),

    # APi's for CUSTOMERS
    url(r'^api/customer/restaurants/$', apis.customer_get_restaurants),
    url(r'^api/customer/meal/(?P<restaurant_id>\d+)/$', apis.customer_get_meals),
    url(r'^api/customer/order/add/$', apis.customer_add_order),
    url(r'^api/customer/order/latest/$', apis.customer_get_latest_order),
    url(r'^api/customer/driver/location/$', apis.customer_get_driver_location),

    # Api's for DRIVERS
    url(r"^api/drivers/orders/ready/$", apis.driver_get_ready_orders),
    url(r"^api/drivers/order/pick/$", apis.driver_pick_order),
    url(r"^api/drivers/order/latest/$", apis.driver_get_latest_order),
    url(r"^api/drivers/order/complete/$", apis.driver_complete_order),
    url(r"^api/drivers/revenue/$", apis.driver_get_revenue),
    url(r"^api/drivers/location/update/$", apis.driver_update_location),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

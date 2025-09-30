"""
URL configuration for KASNEBvms project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.shortcuts import redirect
from main import views as main_views

urlpatterns = [
    path('', lambda request: redirect('login'), name='root'),
    path('admin/', admin.site.urls),
    path('login/', main_views.login_view, name='login'),
    path('dashboard/', main_views.dashboard_view, name='dashboard'),
    path('logout/', main_views.logout_view, name='logout'),
    
    # Visitor management
    path('visitor/register/', main_views.visitor_registration, name='visitor_registration'),
    path('visitor/checkout/<int:visitor_id>/', main_views.visitor_checkout, name='visitor_checkout'),
    path('visitors/', main_views.visitor_list, name='visitor_list'),
    
    # Vehicle management
    path('vehicle/register/', main_views.vehicle_registration, name='vehicle_registration'),
    path('vehicle/departure/<int:vehicle_id>/', main_views.vehicle_departure, name='vehicle_departure'),
    path('vehicles/', main_views.vehicle_list, name='vehicle_list'),
]

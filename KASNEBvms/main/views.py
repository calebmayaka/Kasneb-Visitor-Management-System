from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.http import JsonResponse
from django.core.exceptions import PermissionDenied
from django.conf import settings
from django.db.models import Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
from functools import wraps
from .models import KasnebUser, Visitor, Vehicle

# Create your views here.

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'main/login.html')

def admin_setup(request):
    if not settings.DEBUG:
        raise PermissionDenied

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone_number = request.POST.get('phone_number')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')

        if password != password_confirm:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'main/admin_setup.html')

        if KasnebUser.objects.filter(username=username).exists():
            messages.error(request, 'Username is already taken.')
            return render(request, 'main/admin_setup.html')

        if KasnebUser.objects.filter(email=email).exists():
            messages.error(request, 'Email is already in use.')
            return render(request, 'main/admin_setup.html')

        KasnebUser.objects.create_superuser(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            password=password,
        )
        messages.success(request, 'Admin account created. You can now log in.')
        return redirect('login')

    return render(request, 'main/admin_setup.html')

def role_required(*roles):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            user = request.user
            if user.is_superuser or user.role in roles:
                return view_func(request, *args, **kwargs)
            raise PermissionDenied
        return _wrapped
    return decorator

@login_required
@role_required('security', 'ict_officer', 'admin')
def dashboard_view(request):
    # Get today's statistics
    today = timezone.now().date()
    
    # Visitor statistics
    total_visitors_today = Visitor.objects.filter(check_in_time__date=today).count()
    checked_in_visitors = Visitor.objects.filter(status='checked_in').count()
    checked_out_visitors = Visitor.objects.filter(check_in_time__date=today, status='checked_out').count()
    
    # Vehicle statistics
    total_vehicles_today = Vehicle.objects.filter(entry_time__date=today).count()
    parked_vehicles = Vehicle.objects.filter(status='parked').count()
    departed_vehicles = Vehicle.objects.filter(entry_time__date=today, status='departed').count()
    
    # Recent visitors (last 10)
    recent_visitors = Visitor.objects.all()[:10]
    
    # Recent vehicles (last 10)
    recent_vehicles = Vehicle.objects.all()[:10]
    
    context = {
        'total_visitors_today': total_visitors_today,
        'checked_in_visitors': checked_in_visitors,
        'checked_out_visitors': checked_out_visitors,
        'total_vehicles_today': total_vehicles_today,
        'parked_vehicles': parked_vehicles,
        'departed_vehicles': departed_vehicles,
        'recent_visitors': recent_visitors,
        'recent_vehicles': recent_vehicles,
    }
    
    return render(request, 'main/dashboard.html', context)

@login_required
@role_required('security', 'admin')
def visitor_registration(request):
    if request.method == 'POST':
        try:
            visitor = Visitor.objects.create(
                first_name=request.POST.get('first_name'),
                last_name=request.POST.get('last_name'),
                phone_number=request.POST.get('phone_number'),
                email=request.POST.get('email') or None,
                id_number=request.POST.get('id_number'),
                company_organization=request.POST.get('company_organization') or None,
                host_name=request.POST.get('host_name'),
                host_department=request.POST.get('host_department'),
                visit_purpose=request.POST.get('visit_purpose'),
                visit_purpose_details=request.POST.get('visit_purpose_details') or None,
                items_carried=request.POST.get('items_carried') or None,
                special_requirements=request.POST.get('special_requirements') or None,
                visitor_badge_number=request.POST.get('visitor_badge_number') or None,
                security_officer=request.user
            )
            messages.success(request, f'Visitor {visitor.full_name} registered successfully!')
            return redirect('visitor_registration')
        except Exception as e:
            messages.error(request, f'Error registering visitor: {str(e)}')
    
    return render(request, 'main/visitor_registration.html')

@login_required
@role_required('security', 'admin')
def vehicle_registration(request):
    if request.method == 'POST':
        try:
            # Check if visitor ID is provided to link vehicle to visitor
            visitor = None
            visitor_id = request.POST.get('visitor_id')
            if visitor_id:
                try:
                    visitor = Visitor.objects.get(id=visitor_id)
                except Visitor.DoesNotExist:
                    pass
            
            vehicle = Vehicle.objects.create(
                license_plate=request.POST.get('license_plate').upper(),
                vehicle_type=request.POST.get('vehicle_type'),
                make_model=request.POST.get('make_model') or None,
                color=request.POST.get('color') or None,
                driver_name=request.POST.get('driver_name'),
                driver_phone=request.POST.get('driver_phone'),
                driver_id_number=request.POST.get('driver_id_number'),
                purpose=request.POST.get('purpose'),
                parking_spot=request.POST.get('parking_spot') or None,
                special_notes=request.POST.get('special_notes') or None,
                visitor=visitor,
                security_officer=request.user
            )
            messages.success(request, f'Vehicle {vehicle.license_plate} registered successfully!')
            return redirect('vehicle_registration')
        except Exception as e:
            messages.error(request, f'Error registering vehicle: {str(e)}')
    
    # Get recent visitors for linking
    recent_visitors = Visitor.objects.filter(status='checked_in')[:20]
    
    return render(request, 'main/vehicle_registration.html', {'recent_visitors': recent_visitors})

@login_required
@role_required('security', 'admin')
def visitor_checkout(request, visitor_id):
    visitor = get_object_or_404(Visitor, id=visitor_id)
    if visitor.status == 'checked_in':
        visitor.status = 'checked_out'
        visitor.check_out_time = timezone.now()
        visitor.save()
        messages.success(request, f'{visitor.full_name} checked out successfully!')
    else:
        messages.warning(request, f'{visitor.full_name} is already checked out!')
    return redirect('dashboard')

@login_required
@role_required('security', 'admin')
def vehicle_departure(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)
    if vehicle.status == 'parked':
        vehicle.status = 'departed'
        vehicle.exit_time = timezone.now()
        vehicle.save()
        messages.success(request, f'Vehicle {vehicle.license_plate} marked as departed!')
    else:
        messages.warning(request, f'Vehicle {vehicle.license_plate} has already departed!')
    return redirect('dashboard')

@login_required
@role_required('security', 'ict_officer', 'admin')
def visitor_list(request):
    visitors = Visitor.objects.all()
    
    # Filter by status if provided
    status_filter = request.GET.get('status')
    if status_filter:
        visitors = visitors.filter(status=status_filter)
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        visitors = visitors.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(phone_number__icontains=search_query) |
            Q(id_number__icontains=search_query) |
            Q(host_name__icontains=search_query)
        )
    
    return render(request, 'main/visitor_list.html', {'visitors': visitors})

@login_required
@role_required('security', 'ict_officer', 'admin')
def vehicle_list(request):
    vehicles = Vehicle.objects.all()
    
    # Filter by status if provided
    status_filter = request.GET.get('status')
    if status_filter:
        vehicles = vehicles.filter(status=status_filter)
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        vehicles = vehicles.filter(
            Q(license_plate__icontains=search_query) |
            Q(driver_name__icontains=search_query) |
            Q(driver_phone__icontains=search_query) |
            Q(make_model__icontains=search_query)
        )
    
    return render(request, 'main/vehicle_list.html', {'vehicles': vehicles})

def logout_view(request):
    logout(request)
    return redirect('login')

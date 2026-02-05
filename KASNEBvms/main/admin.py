from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import KasnebUser, Visitor, Vehicle

# Register your models here.

@admin.register(KasnebUser)
class KasnebUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'phone_number', 'role', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'phone_number')
    ordering = ('username',)
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'phone_number', 'role')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login',)}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'first_name', 'last_name', 'phone_number', 'role', 'password1', 'password2'),
        }),
    )

@admin.register(Visitor)
class VisitorAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'phone_number', 'host_name', 'visit_purpose', 'status', 'check_in_time', 'security_officer')
    list_filter = ('status', 'visit_purpose', 'check_in_time', 'security_officer')
    search_fields = ('first_name', 'last_name', 'phone_number', 'id_number', 'host_name', 'company_organization')
    date_hierarchy = 'check_in_time'
    ordering = ('-check_in_time',)
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'phone_number', 'email', 'id_number', 'company_organization')
        }),
        ('Visit Information', {
            'fields': ('host_name', 'host_department', 'visit_purpose', 'visit_purpose_details', 'visitor_badge_number')
        }),
        ('Timestamps', {
            'fields': ('check_in_time', 'check_out_time', 'expected_duration')
        }),
        ('Status & Security', {
            'fields': ('status', 'security_officer')
        }),
        ('Additional Information', {
            'fields': ('items_carried', 'special_requirements'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('license_plate', 'driver_name', 'vehicle_type', 'status', 'entry_time', 'security_officer')
    list_filter = ('status', 'vehicle_type', 'entry_time', 'security_officer')
    search_fields = ('license_plate', 'driver_name', 'driver_phone', 'make_model', 'purpose')
    date_hierarchy = 'entry_time'
    ordering = ('-entry_time',)
    
    fieldsets = (
        ('Vehicle Information', {
            'fields': ('license_plate', 'vehicle_type', 'make_model', 'color')
        }),
        ('Driver Information', {
            'fields': ('driver_name', 'driver_phone', 'driver_id_number')
        }),
        ('Visit Information', {
            'fields': ('visitor', 'purpose', 'parking_spot')
        }),
        ('Timestamps', {
            'fields': ('entry_time', 'exit_time')
        }),
        ('Status & Security', {
            'fields': ('status', 'security_officer')
        }),
        ('Additional Information', {
            'fields': ('special_notes',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone

class KasnebUserManager(BaseUserManager):
    def create_user(self, username, email, first_name, last_name, phone_number, password=None, **extra_fields):
        if not username:
            raise ValueError('The Username must be set')
        if not email:
            raise ValueError('The Email must be set')
        email = self.normalize_email(email)
        user = self.model(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, first_name, last_name, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, email, first_name, last_name, phone_number, password, **extra_fields)

class KasnebUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=150, unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = KasnebUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name', 'phone_number']

    def __str__(self):
        return self.username


class Visitor(models.Model):
    VISIT_PURPOSE_CHOICES = [
        ('meeting', 'Meeting'),
        ('interview', 'Interview'),
        ('delivery', 'Delivery'),
        ('maintenance', 'Maintenance'),
        ('consultation', 'Consultation'),
        ('training', 'Training'),
        ('examination', 'Examination'),
        ('other', 'Other'),
    ]
    
    VISIT_STATUS_CHOICES = [
        ('checked_in', 'Checked In'),
        ('checked_out', 'Checked Out'),
    ]
    
    # Personal Information
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    id_number = models.CharField(max_length=20, unique=True)
    company_organization = models.CharField(max_length=100, blank=True, null=True)
    
    # Visit Information
    host_name = models.CharField(max_length=100)
    host_department = models.CharField(max_length=100)
    visit_purpose = models.CharField(max_length=20, choices=VISIT_PURPOSE_CHOICES)
    visit_purpose_details = models.TextField(blank=True, null=True)
    
    # Timestamps
    check_in_time = models.DateTimeField(default=timezone.now)
    check_out_time = models.DateTimeField(blank=True, null=True)
    expected_duration = models.DurationField(blank=True, null=True)
    
    # Status and Security
    status = models.CharField(max_length=15, choices=VISIT_STATUS_CHOICES, default='checked_in')
    security_officer = models.ForeignKey(KasnebUser, on_delete=models.CASCADE, related_name='registered_visitors')
    visitor_badge_number = models.CharField(max_length=10, blank=True, null=True)
    
    # Additional Information
    items_carried = models.TextField(blank=True, null=True, help_text="List any bags, laptops, or other items")
    special_requirements = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-check_in_time']
        
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.check_in_time.strftime('%Y-%m-%d %H:%M')}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def is_checked_out(self):
        return self.status == 'checked_out'
    
    @property
    def visit_duration(self):
        if self.check_out_time:
            return self.check_out_time - self.check_in_time
        return timezone.now() - self.check_in_time


class Vehicle(models.Model):
    VEHICLE_TYPE_CHOICES = [
        ('car', 'Car'),
        ('motorcycle', 'Motorcycle'),
        ('truck', 'Truck'),
        ('van', 'Van'),
        ('bus', 'Bus'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('parked', 'Parked'),
        ('departed', 'Departed'),
    ]
    
    # Vehicle Information
    license_plate = models.CharField(max_length=20, unique=True)
    vehicle_type = models.CharField(max_length=15, choices=VEHICLE_TYPE_CHOICES)
    make_model = models.CharField(max_length=100, blank=True, null=True)
    color = models.CharField(max_length=30, blank=True, null=True)
    
    # Owner/Driver Information
    driver_name = models.CharField(max_length=100)
    driver_phone = models.CharField(max_length=20)
    driver_id_number = models.CharField(max_length=20)
    
    # Visit Information
    visitor = models.ForeignKey(Visitor, on_delete=models.CASCADE, related_name='vehicles', blank=True, null=True)
    purpose = models.CharField(max_length=200)
    parking_spot = models.CharField(max_length=20, blank=True, null=True)
    
    # Timestamps
    entry_time = models.DateTimeField(default=timezone.now)
    exit_time = models.DateTimeField(blank=True, null=True)
    
    # Status and Security
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='parked')
    security_officer = models.ForeignKey(KasnebUser, on_delete=models.CASCADE, related_name='registered_vehicles')
    
    # Additional Information
    special_notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-entry_time']
        
    def __str__(self):
        return f"{self.license_plate} - {self.driver_name}"
    
    @property
    def is_departed(self):
        return self.status == 'departed'
    
    @property
    def parking_duration(self):
        if self.exit_time:
            return self.exit_time - self.entry_time
        return timezone.now() - self.entry_time

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    ROLE_CHOICES = (
        ('STUDENT', 'Student / Resident'),
        ('STAFF', 'Maintenance Staff / Admin'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='STUDENT')
    phone_number = models.CharField(max_length=20, blank=True, default='')
    department_or_hostel = models.CharField(
        max_length=150, 
        blank=True, 
        default='', 
        help_text="Hostel Name & Room #, or Department/Office"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"

    @property
    def is_staff_member(self):
        return self.role == 'STAFF' or self.user.is_staff or self.user.is_superuser


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        # Avoid creating profile if superuser created via createsuperuser with staff role
        role = 'STAFF' if (instance.is_staff or instance.is_superuser) else 'STUDENT'
        UserProfile.objects.create(user=instance, role=role)
    else:
        if hasattr(instance, 'profile'):
            instance.profile.save()


class MaintenanceRequest(models.Model):
    CATEGORY_CHOICES = (
        ('PLUMBING', 'Plumbing'),
        ('ELECTRICAL', 'Electrical'),
        ('CARPENTRY', 'Carpentry & Furniture'),
        ('HVAC', 'HVAC & Air Conditioning'),
        ('APPLIANCE', 'Appliances'),
        ('INFRASTRUCTURE', 'Building & Infrastructure'),
        ('IT_NETWORKING', 'IT & Wi-Fi'),
        ('OTHER', 'Other'),
    )

    PRIORITY_CHOICES = (
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('URGENT', 'Urgent / Emergency'),
    )

    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('REJECTED', 'Rejected'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='maintenance_requests')
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='OTHER')
    location = models.CharField(max_length=200, help_text="e.g. Hostel Block B - Room 302 or Science Lab 101")
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='MEDIUM')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    date_reported = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    assigned_staff = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='assigned_maintenance_requests'
    )
    resolution_notes = models.TextField(blank=True, null=True, help_text="Notes from maintenance staff")

    class Meta:
        ordering = ['-date_reported']

    def __str__(self):
        return f"[{self.get_status_display()}] {self.title} - {self.location}"

    @property
    def status_color_class(self):
        mapping = {
            'PENDING': 'warning',
            'IN_PROGRESS': 'info',
            'COMPLETED': 'success',
            'REJECTED': 'danger',
        }
        return mapping.get(self.status, 'secondary')

    @property
    def priority_color_class(self):
        mapping = {
            'LOW': 'muted',
            'MEDIUM': 'blue',
            'HIGH': 'orange',
            'URGENT': 'red',
        }
        return mapping.get(self.priority, 'secondary')


class RequestComment(models.Model):
    request = models.ForeignKey(MaintenanceRequest, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {self.user.username} on #{self.request.id}"

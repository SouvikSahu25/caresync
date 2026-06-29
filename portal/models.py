from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    ROLE_CHOICES = (
        ('PATIENT', 'Patient'),
        ('DOCTOR', 'Doctor'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='PATIENT')
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.role}"

class DoctorProfile(models.Model):
    SPECIALIZATION_CHOICES = (
        ('GP', 'General Physician'),
        ('PEDS', 'Pediatrician'),
        ('CARD', 'Cardiologist'),
        ('DERM', 'Dermatologist'),
        ('NEUR', 'Neurologist'),
        ('ORTH', 'Orthopedist'),
    )
    profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE, limit_choices_to={'role': 'DOCTOR'}, related_name='doctor_profile')
    specialization = models.CharField(max_length=10, choices=SPECIALIZATION_CHOICES, default='GP')
    bio = models.TextField(blank=True, null=True)
    fee = models.DecimalField(max_digits=6, decimal_places=2, default=500.00)
    availability = models.CharField(max_length=100, default='Mon-Fri, 9:00 AM - 5:00 PM')

    def __str__(self):
        full_name = self.profile.user.get_full_name()
        name = full_name if full_name else self.profile.user.username
        return f"Dr. {name} ({self.get_specialization_display()})"

class Appointment(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('CANCELLED', 'Cancelled'),
        ('COMPLETED', 'Completed'),
    )
    SLOT_CHOICES = (
        ('MORNING', 'Morning (09:00 AM - 12:00 PM)'),
        ('AFTERNOON', 'Afternoon (01:00 PM - 04:00 PM)'),
        ('EVENING', 'Evening (05:00 PM - 08:00 PM)'),
    )
    patient = models.ForeignKey(UserProfile, on_delete=models.CASCADE, limit_choices_to={'role': 'PATIENT'}, related_name='appointments')
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name='appointments')
    date = models.DateField()
    time_slot = models.CharField(max_length=15, choices=SLOT_CHOICES)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='PENDING')
    symptoms = models.TextField()
    prescription = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Appt for {self.patient.user.username} with {self.doctor} on {self.date}"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    try:
        instance.profile.save()
    except UserProfile.DoesNotExist:
        UserProfile.objects.create(user=instance)

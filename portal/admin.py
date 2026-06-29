from django.contrib import admin
from .models import UserProfile, DoctorProfile, Appointment

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'phone')
    list_filter = ('role',)
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'phone')

@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    list_display = ('get_name', 'specialization', 'fee', 'availability')
    list_filter = ('specialization',)
    search_fields = ('profile__user__username', 'profile__user__first_name', 'profile__user__last_name', 'specialization')

    def get_name(self, obj):
        return obj.profile.user.get_full_name() or obj.profile.user.username
    get_name.short_description = 'Doctor Name'

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'date', 'time_slot', 'status')
    list_filter = ('status', 'date', 'time_slot')
    search_fields = ('patient__user__username', 'doctor__profile__user__username', 'symptoms')

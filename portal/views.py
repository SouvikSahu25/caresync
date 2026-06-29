from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import datetime
from .models import UserProfile, DoctorProfile, Appointment

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    specializations = DoctorProfile.SPECIALIZATION_CHOICES
    
    if request.method == 'POST':
        # Get common details
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role') # PATIENT or DOCTOR
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        
        # Validation
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return render(request, 'auth.html', {'specializations': specializations, 'tab': 'register'})
        
        # Create standard User
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        
        # Signal already created the profile. Let's fetch it and update.
        profile = user.profile
        profile.role = role
        profile.phone = phone
        profile.address = address
        profile.save()
        
        # If doctor, create DoctorProfile
        if role == 'DOCTOR':
            specialization = request.POST.get('specialization')
            bio = request.POST.get('bio')
            fee = request.POST.get('fee', 500.00)
            availability = request.POST.get('availability', 'Mon-Fri, 9:00 AM - 5:00 PM')
            
            DoctorProfile.objects.create(
                profile=profile,
                specialization=specialization,
                bio=bio,
                fee=fee,
                availability=availability
            )
            
        # Log user in
        login(request, user)
        messages.success(request, f"Welcome to CareSync, {user.first_name or user.username}!")
        return redirect('dashboard')
        
    return render(request, 'auth.html', {'specializations': specializations, 'tab': 'register'})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password.")
            
    return render(request, 'auth.html', {'tab': 'login'})

@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')

@login_required
def dashboard_view(request):
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        # Create it just in case
        profile = UserProfile.objects.create(user=request.user)
        
    if profile.role == 'DOCTOR':
        return redirect('doctor_dashboard')
    return redirect('patient_dashboard')

@login_required
def patient_dashboard(request):
    profile = request.user.profile
    if profile.role != 'PATIENT':
        return redirect('dashboard')
        
    appointments = Appointment.objects.filter(patient=profile).order_by('-date', '-created_at')
    doctors = DoctorProfile.objects.all().select_related('profile__user')
    slots = Appointment.SLOT_CHOICES
    
    context = {
        'profile': profile,
        'appointments': appointments,
        'doctors': doctors,
        'slots': slots,
    }
    return render(request, 'patient_dashboard.html', context)

@login_required
def doctor_dashboard(request):
    profile = request.user.profile
    if profile.role != 'DOCTOR':
        return redirect('dashboard')
        
    doctor_profile = profile.doctor_profile
    appointments = Appointment.objects.filter(doctor=doctor_profile).order_by('-date', '-created_at')
    
    # Simple statistics
    total_appointments = appointments.count()
    pending_appointments = appointments.filter(status='PENDING').count()
    completed_appointments = appointments.filter(status='COMPLETED').count()
    
    context = {
        'profile': profile,
        'doctor': doctor_profile,
        'appointments': appointments,
        'total': total_appointments,
        'pending': pending_appointments,
        'completed': completed_appointments,
    }
    return render(request, 'doctor_dashboard.html', context)

@login_required
def book_appointment(request):
    if request.method == 'POST':
        profile = request.user.profile
        if profile.role != 'PATIENT':
            messages.error(request, "Only patients can book appointments.")
            return redirect('dashboard')
            
        doctor_id = request.POST.get('doctor_id')
        date_str = request.POST.get('date')
        time_slot = request.POST.get('time_slot')
        symptoms = request.POST.get('symptoms')
        
        doctor = get_object_or_404(DoctorProfile, id=doctor_id)
        
        try:
            # Parse date string to python date object
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
            
            # Simple validation: Prevent booking in the past
            if date_obj < datetime.now().date():
                messages.error(request, "You cannot book an appointment in the past.")
                return redirect('dashboard')
                
            # Prevent double booking: Doctor already has an approved appointment in this slot
            existing = Appointment.objects.filter(
                doctor=doctor,
                date=date_obj,
                time_slot=time_slot,
                status__in=['PENDING', 'APPROVED']
            ).exists()
            
            if existing:
                messages.warning(request, "This time slot is already requested or booked with Dr. " + doctor.profile.user.username + ".")
                return redirect('dashboard')
                
            # Create appointment
            Appointment.objects.create(
                patient=profile,
                doctor=doctor,
                date=date_obj,
                time_slot=time_slot,
                symptoms=symptoms
            )
            messages.success(request, "Appointment requested successfully! Wait for doctor approval.")
        except Exception as e:
            messages.error(request, f"Error booking appointment: {e}")
            
    return redirect('dashboard')

@login_required
def update_appointment(request, appointment_id):
    if request.method == 'POST':
        profile = request.user.profile
        if profile.role != 'DOCTOR':
            messages.error(request, "Only doctors can update appointments.")
            return redirect('dashboard')
            
        appointment = get_object_or_404(Appointment, id=appointment_id, doctor=profile.doctor_profile)
        action = request.POST.get('action') # APPROVE, CANCEL, COMPLETE
        
        if action == 'APPROVE':
            appointment.status = 'APPROVED'
            messages.success(request, "Appointment has been approved!")
        elif action == 'CANCEL':
            appointment.status = 'CANCEL'
            messages.warning(request, "Appointment has been cancelled.")
        elif action == 'COMPLETE':
            prescription = request.POST.get('prescription')
            appointment.prescription = prescription
            appointment.status = 'COMPLETED'
            messages.success(request, "Prescription saved and appointment completed successfully!")
            
        appointment.save()
        
    return redirect('dashboard')

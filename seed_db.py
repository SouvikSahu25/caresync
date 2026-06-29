import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'caresync_project.settings')
django.setup()

from django.contrib.auth.models import User
from portal.models import UserProfile, DoctorProfile, Appointment
from datetime import date, timedelta

def seed():
    print("Seeding database...")
    
    # 1. Create superuser
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@caresync.com', 'admin123', first_name='System', last_name='Administrator')
        print("Created superuser: admin / admin123")
    else:
        print("Superuser 'admin' already exists.")
        
    # 2. Create Doctor
    if not User.objects.filter(username='dr_smith').exists():
        doc_user = User.objects.create_user('dr_smith', 'smith@caresync.com', 'doctor123', first_name='John', last_name='Smith')
        # User profile gets created by signal. Let's fetch it:
        profile = doc_user.profile
        profile.role = 'DOCTOR'
        profile.phone = '9876543210'
        profile.address = 'Cardiology Dept, Clinic Block A'
        profile.save()
        
        DoctorProfile.objects.create(
            profile=profile,
            specialization='CARD', # Cardiologist
            bio='Dr. John Smith is a board-certified Cardiologist with over 15 years of experience in cardiovascular sciences.',
            fee=800.00,
            availability='Mon-Wed, 10:00 AM - 4:00 PM'
        )
        print("Created doctor user: dr_smith / doctor123")
    else:
        print("Doctor 'dr_smith' already exists.")
        
    # 3. Create another Doctor (General Physician)
    if not User.objects.filter(username='dr_jones').exists():
        doc_user2 = User.objects.create_user('dr_jones', 'jones@caresync.com', 'doctor123', first_name='Sarah', last_name='Jones')
        profile2 = doc_user2.profile
        profile2.role = 'DOCTOR'
        profile2.phone = '9876543211'
        profile2.address = 'General Outpatient Dept'
        profile2.save()
        
        DoctorProfile.objects.create(
            profile=profile2,
            specialization='GP', # General Physician
            bio='Dr. Sarah Jones specializes in family medicine and preventative care services.',
            fee=500.00,
            availability='Tue-Fri, 9:00 AM - 3:00 PM'
        )
        print("Created doctor user: dr_jones / doctor123")
    else:
        print("Doctor 'dr_jones' already exists.")
        
    # 4. Create Patient
    if not User.objects.filter(username='patient_alice').exists():
        pat_user = User.objects.create_user('patient_alice', 'alice@gmail.com', 'patient123', first_name='Alice', last_name='Cooper')
        profile = pat_user.profile
        profile.role = 'PATIENT'
        profile.phone = '1234567890'
        profile.address = '742 Evergreen Terrace, Springfield'
        profile.save()
        print("Created patient user: patient_alice / patient123")
    else:
        print("Patient 'patient_alice' already exists.")
        
    # 5. Create some initial appointments
    alice_profile = User.objects.get(username='patient_alice').profile
    smith_profile = DoctorProfile.objects.get(profile__user__username='dr_smith')
    jones_profile = DoctorProfile.objects.get(profile__user__username='dr_jones')
    
    if not Appointment.objects.filter(patient=alice_profile).exists():
        # Create a pending appointment with Dr. Smith
        Appointment.objects.create(
            patient=alice_profile,
            doctor=smith_profile,
            date=date.today() + timedelta(days=2),
            time_slot='MORNING',
            symptoms='Mild chest pain and shortness of breath during light workouts.'
        )
        
        # Create a completed appointment with Dr. Jones
        completed_appt = Appointment.objects.create(
            patient=alice_profile,
            doctor=jones_profile,
            date=date.today() - timedelta(days=5),
            time_slot='AFTERNOON',
            status='COMPLETED',
            symptoms='Seasonal allergies, runny nose, and constant sneezing.',
            prescription='Take Cetirizine 10mg once daily at bedtime for 7 days. Stay hydrated.'
        )
        print("Created sample appointments for patient_alice.")
    else:
        print("Sample appointments already exist.")
        
    print("Database seeding completed successfully!")

if __name__ == '__main__':
    seed()

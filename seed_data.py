import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'campus_maintenance.settings')
django.setup()

from django.contrib.auth.models import User
from maintenance.models import UserProfile, MaintenanceRequest, RequestComment

def seed():
    print("Seeding database...")

    # 1. Create Admin User
    admin, created = User.objects.get_or_create(username='admin', defaults={
        'first_name': 'Admin',
        'last_name': 'Officer',
        'email': 'admin@campus.edu',
        'is_staff': True,
        'is_superuser': True
    })
    if created:
        admin.set_password('admin123')
        admin.save()
        print("Created Superuser 'admin' / 'admin123'")

    # 2. Create Staff Members
    staff1, created = User.objects.get_or_create(username='staff_john', defaults={
        'first_name': 'John',
        'last_name': 'Smith (Electrical Engineer)',
        'email': 'john.smith@campus.edu',
        'is_staff': True
    })
    if created:
        staff1.set_password('staff123')
        staff1.save()
        staff1.profile.role = 'STAFF'
        staff1.profile.department_or_hostel = 'Campus Electrical & Facilities Dept'
        staff1.profile.phone_number = '+1 (555) 123-4567'
        staff1.profile.save()
        print("Created Staff 'staff_john' / 'staff123'")

    staff2, created = User.objects.get_or_create(username='staff_sarah', defaults={
        'first_name': 'Sarah',
        'last_name': 'Jenkins (Plumbing Lead)',
        'email': 'sarah.jenkins@campus.edu',
        'is_staff': True
    })
    if created:
        staff2.set_password('staff123')
        staff2.save()
        staff2.profile.role = 'STAFF'
        staff2.profile.department_or_hostel = 'Plumbing & Water Services'
        staff2.profile.phone_number = '+1 (555) 987-6543'
        staff2.profile.save()
        print("Created Staff 'staff_sarah' / 'staff123'")

    # 3. Create Students
    student1, created = User.objects.get_or_create(username='alex_student', defaults={
        'first_name': 'Alex',
        'last_name': 'Morgan',
        'email': 'alex.m@student.campus.edu'
    })
    if created:
        student1.set_password('student123')
        student1.save()
        student1.profile.role = 'STUDENT'
        student1.profile.department_or_hostel = 'Hostel Block B - Room 304'
        student1.profile.phone_number = '+1 (555) 234-5678'
        student1.profile.save()
        print("Created Student 'alex_student' / 'student123'")

    student2, created = User.objects.get_or_create(username='emma_student', defaults={
        'first_name': 'Emma',
        'last_name': 'Watson',
        'email': 'emma.w@student.campus.edu'
    })
    if created:
        student2.set_password('student123')
        student2.save()
        student2.profile.role = 'STUDENT'
        student2.profile.department_or_hostel = 'Hostel Block A - Room 112'
        student2.profile.phone_number = '+1 (555) 345-6789'
        student2.profile.save()
        print("Created Student 'emma_student' / 'student123'")

    # 4. Create Maintenance Requests
    requests_data = [
        {
            'user': student1,
            'title': 'Leaking Tap in Hostel Washroom',
            'description': 'The hot water tap in Hostel Block B, 3rd Floor washroom is constantly leaking water creating a puddle.',
            'category': 'PLUMBING',
            'location': 'Hostel Block B - 3rd Floor Washroom',
            'priority': 'HIGH',
            'status': 'IN_PROGRESS',
            'assigned_staff': staff2,
            'resolution_notes': 'Plumber dispatched with replacement washer valves.'
        },
        {
            'user': student1,
            'title': 'Study Lamp Power Socket Sparking',
            'description': 'The wall socket near desk #2 in Room 304 sparked when plugging in a laptop charger. Needs urgent safety inspection.',
            'category': 'ELECTRICAL',
            'location': 'Hostel Block B - Room 304',
            'priority': 'URGENT',
            'status': 'PENDING',
            'assigned_staff': staff1,
            'resolution_notes': ''
        },
        {
            'user': student2,
            'title': 'Broken Door Handle on Science Lab 102',
            'description': 'The main entrance door latch is jammed and does not shut completely.',
            'category': 'CARPENTRY',
            'location': 'Science Building - Lab 102',
            'priority': 'MEDIUM',
            'status': 'COMPLETED',
            'assigned_staff': staff1,
            'resolution_notes': 'Replaced broken lock barrel and lubed door hinges.'
        },
        {
            'user': student2,
            'title': 'AC Unit Blowing Warm Air',
            'description': 'Air conditioner unit in Study Room 4 is not cooling properly and making a buzzing noise.',
            'category': 'HVAC',
            'location': 'Library 2nd Floor - Study Room 4',
            'priority': 'MEDIUM',
            'status': 'IN_PROGRESS',
            'assigned_staff': staff1,
            'resolution_notes': 'Cleaned air filters; checking refrigerant gas pressure.'
        },
        {
            'user': student1,
            'title': 'Wi-Fi Access Point Offline',
            'description': 'The Wi-Fi router on the 3rd floor corridor has a blinking orange light and no student devices can connect.',
            'category': 'IT_NETWORKING',
            'location': 'Hostel Block B - Corridor 3',
            'priority': 'HIGH',
            'status': 'COMPLETED',
            'assigned_staff': staff1,
            'resolution_notes': 'Rebooted access point switch and verified gateway IP routing.'
        },
    ]

    for data in requests_data:
        req, created_req = MaintenanceRequest.objects.get_or_create(
            title=data['title'],
            user=data['user'],
            defaults=data
        )
        if created_req:
            # Add sample comments
            RequestComment.objects.create(
                request=req,
                user=req.user,
                comment=f"Initial request logged by {req.user.first_name}. Please inspect as soon as available."
            )
            if req.assigned_staff:
                RequestComment.objects.create(
                    request=req,
                    user=req.assigned_staff,
                    comment=f"Hi {req.user.first_name}, I have been assigned to this ticket and will visit the site."
                )

    print("Database seeding completed successfully!")

if __name__ == '__main__':
    seed()

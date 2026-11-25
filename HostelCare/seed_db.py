import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hostel_complaints.settings')
django.setup()

from django.contrib.auth.models import User
from complaints.models import Profile, Complaint, Comment, Hostel

def seed():
    print("Seeding database...")
    
    # 1. Create Warden (Superuser)
    warden_user, created = User.objects.get_or_create(username='admin', email='admin@hostelcare.com')
    if created:
        warden_user.set_password('admin123')
        warden_user.is_superuser = True
        warden_user.is_staff = True
        warden_user.save()
        print("Created warden (admin/admin123)")
    
    warden_profile = warden_user.profile
    warden_profile.role = 'warden'
    warden_profile.phone = '9876543210'
    warden_profile.save()

    # 2. Create Default Hostel
    hostel, created = Hostel.objects.get_or_create(
        code='ABC7X92K',
        defaults={'name': 'ABC Boys Hostel', 'warden': warden_user}
    )
    if not created and hostel.warden != warden_user:
        hostel.warden = warden_user
        hostel.save()
    print(f"Hostel '{hostel.name}' ready with Key: {hostel.code}")

    # 3. Create Student
    student_user, created = User.objects.get_or_create(username='student', email='student@hostelcare.com')
    if created:
        student_user.set_password('student123')
        student_user.save()
        print("Created student (student/student123)")
        
    student_profile = student_user.profile
    student_profile.role = 'student'
    student_profile.hostel = hostel
    student_profile.roll_no = 'CS10245'
    student_profile.room_no = '304-B'
    student_profile.hostel_block = hostel.name
    student_profile.phone = '9123456789'
    student_profile.save()

    # Clear old complaints to keep it fresh
    Complaint.objects.all().delete()

    # 4. Create Sample Complaints
    # Complaint 1: Pending Plumbing Issue
    c1 = Complaint.objects.create(
        student=student_user,
        hostel=hostel,
        title='Water leak in bathroom faucet',
        category='plumbing',
        priority='high',
        description='There is a constant water drip from the washbasin faucet, causing water logging in the washroom. Please repair as soon as possible.',
        room_no='304-B',
        hostel_block=hostel.name,
        status='pending'
    )
    print("Created pending complaint #1")

    # Complaint 2: In Progress Electrical Issue
    c2 = Complaint.objects.create(
        student=student_user,
        hostel=hostel,
        title='Ceiling fan making squeaking noise',
        category='electrical',
        priority='medium',
        description='The ceiling fan in the room makes a loud squeaking sound on speed 4 and 5. It is impossible to study or sleep with the noise.',
        room_no='304-B',
        hostel_block=hostel.name,
        status='in_progress',
        assigned_staff='Ravi Kumar (Electrician)'
    )
    Comment.objects.create(
        complaint=c2,
        author=warden_user,
        message="I have assigned Ravi, the resident electrician, to look into this tomorrow morning. Keep your room open.",
        is_internal=False
    )
    Comment.objects.create(
        complaint=c2,
        author=student_user,
        message="Thank you warden. I will be in the room till 11:00 AM.",
        is_internal=False
    )
    print("Created in_progress complaint #2")

    # Complaint 3: Resolved WiFi Issue
    c3 = Complaint.objects.create(
        student=student_user,
        hostel=hostel,
        title='WiFi router disconnects repeatedly',
        category='wifi',
        priority='high',
        description='The hostel WiFi router on the 3rd floor corridor drops connection every 10 minutes. Tried restarting, but the issue persists.',
        room_no='304-B',
        hostel_block=hostel.name,
        status='resolved',
        assigned_staff='SysNet Solutions Team'
    )
    Comment.objects.create(
        complaint=c3,
        author=warden_user,
        message="IT team reports that the router firmware has been updated and the cable replaced.",
        is_internal=False
    )
    print("Created resolved complaint #3")

    # Complaint 4: Closed Carpentry Issue
    c4 = Complaint.objects.create(
        student=student_user,
        hostel=hostel,
        title='Broken wardrobe handle',
        category='carpentry',
        priority='low',
        description='The handle of the left wardrobe doors is broken and needs replacement.',
        room_no='304-B',
        hostel_block=hostel.name,
        status='closed',
        assigned_staff='Mohan (Carpenter)',
        rating=5,
        feedback='Mohan replaced the handle within a few hours. Excellent and prompt service!'
    )
    print("Created closed complaint #4")
    
    print("\nDatabase seeded successfully!")
    print("Login credentials:")
    print("  Warden: admin / admin123 (Hostel Key: ABC7X92K)")
    print("  Student: student / student123")

if __name__ == '__main__':
    seed()


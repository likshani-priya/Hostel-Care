import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hostel_complaints.settings')
django.setup()

from django.test import Client, override_settings
from django.contrib.auth.models import User
from django.core import mail
from complaints.models import Profile, Hostel, Complaint, generate_hostel_key

@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
def run_tests():
    print("==================================================")
    print("    RUNNING AUTOMATED TEST SUITE FOR HOSTELCARE   ")
    print("==================================================\n")

    # Cleanup test data from previous runs
    User.objects.filter(username__in=['student_valid', 'student_invalid', 'warden2', 'student_beta']).delete()
    Hostel.objects.filter(name__in=['Test Hostel Alpha', 'Test Hostel Beta']).delete()

    client = Client()

    # TEST 1: Student login role badge & display_role
    print("[TEST 1] Verifying Student role badge...")
    student_user = User.objects.get(username='student')
    assert student_user.profile.display_role == "Student", f"Expected Student, got {student_user.profile.display_role}"
    assert student_user.profile.role_badge_class == "student", f"Expected student, got {student_user.profile.role_badge_class}"
    print("-> PASSED: Student profile correctly displays 'Student'\n")

    # TEST 2: Warden login role badge & display_role
    print("[TEST 2] Verifying Warden role badge...")
    admin_user = User.objects.get(username='admin')
    assert admin_user.profile.display_role == "Warden", f"Expected Warden, got {admin_user.profile.display_role}"
    assert admin_user.profile.role_badge_class == "warden", f"Expected warden, got {admin_user.profile.role_badge_class}"
    print("-> PASSED: Warden profile correctly displays 'Warden'\n")

    # TEST 3: Warden Dashboard Heading
    print("[TEST 3] Verifying Warden Dashboard Heading...")
    client.login(username='admin', password='admin123')
    response = client.get('/dashboard/warden/')
    assert response.status_code == 200
    assert b"Warden Dashboard" in response.content, "Heading 'Warden Dashboard' not found in response!"
    assert b"Warden Administration" not in response.content, "Old heading 'Warden Administration' still present!"
    print("-> PASSED: Visible heading is 'Warden Dashboard'\n")

    # TEST 4: Create Hostel & Unique Hostel Key
    print("[TEST 4] Verifying Hostel creation & unique key generation...")
    key1 = generate_hostel_key()
    hostel1 = Hostel.objects.create(name='Test Hostel Alpha', code=key1, warden=admin_user)
    assert len(hostel1.code) == 8, f"Key length should be 8, got {len(hostel1.code)}"
    assert hostel1.code.isalnum(), "Hostel Key should be alphanumeric"
    print(f"-> PASSED: Created Hostel '{hostel1.name}' with key: {hostel1.code}\n")

    # TEST 5: Student Registration with valid Hostel Key
    print("[TEST 5] Verifying Registration with valid Hostel Key...")
    reg_data = {
        'username': 'student_valid',
        'email': 'student_valid@test.com',
        'password1': 'Pass12345!',
        'password2': 'Pass12345!',
        'role': 'student',
        'hostel_key': hostel1.code,
        'roll_no': 'CS2001',
        'room_no': '101',
    }
    client.logout()
    resp = client.post('/register/', reg_data)
    assert resp.status_code == 302, f"Expected redirect, got status {resp.status_code}"
    new_student = User.objects.get(username='student_valid')
    assert new_student.profile.hostel == hostel1, "Student was not linked to hostel!"
    print(f"-> PASSED: Student '{new_student.username}' registered and linked to '{hostel1.name}'\n")

    # TEST 6: Student Registration with invalid Hostel Key
    print("[TEST 6] Verifying Registration with invalid Hostel Key...")
    invalid_reg_data = {
        'username': 'student_invalid',
        'email': 'student_invalid@test.com',
        'password1': 'Pass12345!',
        'password2': 'Pass12345!',
        'role': 'student',
        'hostel_key': 'INVALID_KEY',
        'roll_no': 'CS2002',
        'room_no': '102',
    }
    client.logout()
    resp = client.post('/register/', invalid_reg_data)
    assert resp.status_code == 200, "Registration should remain on form with error"
    assert b"Invalid Hostel Key" in resp.content, "Expected error message 'Invalid Hostel Key' not rendered"
    assert not User.objects.filter(username='student_invalid').exists(), "User should NOT be created on invalid key"
    print("-> PASSED: Invalid key registration blocked with correct error message\n")

    # TEST 7: Student Submits Complaint -> Linked to Student & Hostel
    print("[TEST 7] Verifying Complaint creation linkage...")
    client.login(username='student_valid', password='Pass12345!')
    complaint_data = {
        'title': 'Test Light Bulb Broken',
        'category': 'electrical',
        'priority': 'medium',
        'description': 'Light bulb in room 101 fused.',
        'room_no': '101',
        'hostel_block': hostel1.name,
    }
    resp = client.post('/complaint/new/', complaint_data)
    assert resp.status_code == 302
    created_complaint = Complaint.objects.get(title='Test Light Bulb Broken')
    assert created_complaint.student == new_student
    assert created_complaint.hostel == hostel1
    print(f"-> PASSED: Complaint #{created_complaint.id} linked to Student '{new_student.username}' and Hostel '{hostel1.name}'\n")

    # TEST 8 & TEST 12: Warden Complaint Filtering & Multi-Hostel Security
    print("[TEST 8 & 12] Verifying Warden Multi-Hostel Complaint Filtering...")
    # Create Warden 2 & Hostel 2
    warden2_user = User.objects.create_user(username='warden2', email='warden2@test.com', password='warden2password')
    warden2_user.profile.role = 'warden'
    warden2_user.profile.save()

    key2 = generate_hostel_key()
    hostel2 = Hostel.objects.create(name='Test Hostel Beta', code=key2, warden=warden2_user)

    # Register student in Hostel 2
    student2 = User.objects.create_user(username='student_beta', email='student_beta@test.com', password='student2password')
    student2.profile.role = 'student'
    student2.profile.hostel = hostel2
    student2.profile.save()

    complaint_hostel2 = Complaint.objects.create(
        student=student2,
        hostel=hostel2,
        title='Hostel 2 Plumbing Problem',
        category='plumbing',
        priority='high',
        description='Water issue in Beta hostel',
        room_no='202',
        hostel_block=hostel2.name,
        status='pending'
    )

    # Login Warden 2 -> Should see ONLY Hostel 2 complaints
    client.login(username='warden2', password='warden2password')
    resp = client.get('/dashboard/warden/')
    assert resp.status_code == 200
    assert b"Hostel 2 Plumbing Problem" in resp.content
    assert b"Test Light Bulb Broken" not in resp.content, "Warden 2 should NOT see Hostel 1 complaints!"
    print("-> PASSED: Warden 2 sees strictly Hostel 2 complaints, Hostel 1 complaints excluded\n")

    # TEST 9, 10, 11: Email Notification Workflow & Anti-Duplication
    print("[TEST 9, 10, 11] Verifying Email Notification Workflow & Anti-Duplication...")
    if not hasattr(mail, 'outbox'):
        mail.outbox = []
    mail.outbox.clear()
    
    # Login Warden 1
    client.login(username='admin', password='admin123')

    # Status update: Pending -> In Progress (No email)
    client.post(f'/complaint/{created_complaint.id}/', {
        'action_type': 'update_complaint',
        'status': 'in_progress',
        'priority': 'medium',
        'assigned_staff': 'Technician Jack'
    })
    created_complaint.refresh_from_db()
    assert created_complaint.status == 'in_progress'
    assert len(mail.outbox) == 0, f"Expected 0 emails for Pending -> In Progress, got {len(mail.outbox)}"
    print("-> Sub-test 9 PASSED: Pending -> In Progress sent NO email")

    # Status update: In Progress -> Resolved (SEND EMAIL)
    client.post(f'/complaint/{created_complaint.id}/', {
        'action_type': 'update_complaint',
        'status': 'resolved',
        'priority': 'medium',
        'assigned_staff': 'Technician Jack'
    })
    created_complaint.refresh_from_db()
    assert created_complaint.status == 'resolved'
    assert len(mail.outbox) == 1, f"Expected 1 email for In Progress -> Resolved, got {len(mail.outbox)}"
    sent_email = mail.outbox[0]
    assert sent_email.subject == "Hostel Complaint Resolved"
    assert new_student.email in sent_email.to
    assert "Test Light Bulb Broken" in sent_email.body
    print("-> Sub-test 10 PASSED: In Progress -> Resolved SENT email to student")

    # Status update: Resolved -> Resolved (Refresh/Resave -> NO email)
    client.post(f'/complaint/{created_complaint.id}/', {
        'action_type': 'update_complaint',
        'status': 'resolved',
        'priority': 'medium',
        'assigned_staff': 'Technician Jack'
    })
    assert len(mail.outbox) == 1, f"Expected still 1 email for Resolved -> Resolved re-save, got {len(mail.outbox)}"
    print("-> Sub-test 11 PASSED: Resolved -> Resolved re-save produced NO duplicate email\n")

    print("==================================================")
    print("    ALL 12 TEST CASES PASSED SUCCESSFULLY!        ")
    print("==================================================")

if __name__ == '__main__':
    run_tests()

from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Profile, Complaint, Comment

class HostelComplaintSystemTests(TestCase):
    def setUp(self):
        # 1. Create a Student user
        self.student_user = User.objects.create_user(
            username='student1',
            email='student1@example.com',
            password='testpassword123'
        )
        self.student_profile = self.student_user.profile
        self.student_profile.role = 'student'
        self.student_profile.roll_no = 'ROLL101'
        self.student_profile.room_no = '302-A'
        self.student_profile.hostel_block = 'Block A'
        self.student_profile.phone = '1234567890'
        self.student_profile.save()

        # 2. Create a Warden user
        self.warden_user = User.objects.create_user(
            username='warden1',
            email='warden1@example.com',
            password='testpassword123'
        )
        self.warden_profile = self.warden_user.profile
        self.warden_profile.role = 'warden'
        self.warden_profile.save()

    def test_profile_creation_signals(self):
        # Verify signal created profile automatically
        user = User.objects.create_user(
            username='temp_user',
            password='temp_password'
        )
        self.assertIsNotNone(user.profile)
        self.assertEqual(user.profile.role, 'student')  # Default role is student

    def test_student_complaint_creation(self):
        # Authenticate student
        self.client.login(username='student1', password='testpassword123')
        
        # Post a complaint
        response = self.client.post(reverse('create_complaint'), {
            'title': 'Leaking Pipe',
            'category': 'plumbing',
            'priority': 'high',
            'description': 'Water is leaking from the bathroom faucet.',
            'room_no': '302-A',
            'hostel_block': 'Block A',
        })
        
        # Check redirect to dashboard after success
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('dashboard'))
        
        # Verify db persistence
        complaint = Complaint.objects.first()
        self.assertIsNotNone(complaint)
        self.assertEqual(complaint.title, 'Leaking Pipe')
        self.assertEqual(complaint.student, self.student_user)
        self.assertEqual(complaint.status, 'pending')

    def test_warden_only_access(self):
        # Try to access warden dashboard as a student - should redirect to student dashboard
        self.client.login(username='student1', password='testpassword123')
        response = self.client.get(reverse('warden_dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse('student_dashboard')))

        # Access warden dashboard as warden - should return 200 OK
        self.client.login(username='warden1', password='testpassword123')
        response = self.client.get(reverse('warden_dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_comment_posting(self):
        # File a complaint
        complaint = Complaint.objects.create(
            student=self.student_user,
            title='Fan Issue',
            category='electrical',
            priority='medium',
            description='Fan is rotating very slowly.',
            room_no='302-A',
            hostel_block='Block A',
            status='pending'
        )

        # Log in as warden
        self.client.login(username='warden1', password='testpassword123')

        # Post an internal comment
        response = self.client.post(reverse('complaint_detail', args=[complaint.id]), {
            'action_type': 'add_comment',
            'message': 'Warden checking internal notes.',
            'is_internal': True
        })
        self.assertRedirects(response, reverse('complaint_detail', args=[complaint.id]))

        # Verify comment
        comment = Comment.objects.first()
        self.assertIsNotNone(comment)
        self.assertTrue(comment.is_internal)
        self.assertEqual(comment.author, self.warden_user)

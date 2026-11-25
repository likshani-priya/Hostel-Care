import secrets
import string
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

ROLE_CHOICES = (
    ('student', 'Student'),
    ('warden', 'Warden'),
)

CATEGORY_CHOICES = (
    ('electrical', 'Electrical & Power'),
    ('plumbing', 'Plumbing & Water'),
    ('housekeeping', 'Housekeeping & Cleaning'),
    ('wifi', 'Wi-Fi & Internet'),
    ('mess', 'Mess & Food'),
    ('carpentry', 'Carpentry & Furniture'),
    ('others', 'Others'),
)

PRIORITY_CHOICES = (
    ('low', 'Low'),
    ('medium', 'Medium'),
    ('high', 'High'),
)

STATUS_CHOICES = (
    ('pending', 'Pending'),
    ('in_progress', 'In Progress'),
    ('resolved', 'Resolved'),
    ('closed', 'Closed'),
)

class Hostel(models.Model):
    name = models.CharField(max_length=100, verbose_name="Hostel Name")
    code = models.CharField(max_length=20, unique=True, verbose_name="Hostel Key")
    warden = models.ForeignKey(User, on_delete=models.CASCADE, related_name='managed_hostels')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.code})"

def generate_hostel_key():
    while True:
        key = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
        if not Hostel.objects.filter(code=key).exists():
            return key

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    hostel = models.ForeignKey(Hostel, on_delete=models.SET_NULL, null=True, blank=True, related_name='students')
    roll_no = models.CharField(max_length=20, blank=True, verbose_name="Roll Number")
    room_no = models.CharField(max_length=10, blank=True, verbose_name="Room Number")
    hostel_block = models.CharField(max_length=30, blank=True, verbose_name="Hostel Block / Name")
    phone = models.CharField(max_length=15, blank=True, verbose_name="Phone Number")
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    @property
    def is_warden(self):
        return self.role == 'warden' or self.user.is_superuser or self.user.is_staff

    @property
    def display_role(self):
        if self.is_warden:
            return "Warden"
        return "Student"

    @property
    def role_badge_class(self):
        if self.is_warden:
            return "warden"
        return "student"

    def __str__(self):
        return f"{self.user.username} ({self.display_role})"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

class Complaint(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='complaints')
    hostel = models.ForeignKey(Hostel, on_delete=models.SET_NULL, null=True, blank=True, related_name='complaints')
    title = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='others')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    description = models.TextField()
    room_no = models.CharField(max_length=10, verbose_name="Room Number")
    hostel_block = models.CharField(max_length=30, verbose_name="Hostel Block")
    attachment = models.ImageField(upload_to='complaints/', blank=True, null=True, verbose_name="Photo Proof")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    assigned_staff = models.CharField(max_length=100, blank=True, verbose_name="Assigned Staff / Technician")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    rating = models.IntegerField(blank=True, null=True, choices=[(i, str(i)) for i in range(1, 6)], verbose_name="Resolution Rating")
    feedback = models.TextField(blank=True, verbose_name="Feedback Details")

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"#{self.id} - {self.title} ({self.get_status_display()})"

class Comment(models.Model):
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_internal = models.BooleanField(default=False, verbose_name="Internal Warden Note")

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        sender_role = self.author.profile.display_role if hasattr(self.author, 'profile') else 'User'
        return f"Comment by {self.author.username} ({sender_role}) on Complaint #{self.complaint.id}"


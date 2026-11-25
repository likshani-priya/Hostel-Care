from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.db.models import Count, Q, Avg
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
import json

from .models import Profile, Complaint, Comment, Hostel, generate_hostel_key
from .forms import RegistrationForm, ComplaintForm, WardenComplaintActionForm, CommentForm, FeedbackForm, HostelForm

# Helper: Check if user is warden
def is_warden(user):
    return user.is_authenticated and (user.is_superuser or user.is_staff or (hasattr(user, 'profile') and user.profile.is_warden))

# Helper: Send resolution email to student
def send_resolution_email(complaint):
    student = complaint.student
    recipient_email = student.email
    if not recipient_email:
        return

    student_name = student.first_name or student.username
    subject = "Hostel Complaint Resolved"
    message = (
        f"Dear {student_name},\n\n"
        f"Your hostel maintenance complaint has been resolved successfully.\n\n"
        f"Complaint:\n"
        f"{complaint.title}\n\n"
        f"Status:\n"
        f"Resolved\n\n"
        f"Thank you,\n"
        f"HostelCare Hostel Management System"
    )
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient_email],
            fail_silently=True,
        )
    except Exception:
        pass

# Landing Page
def landing(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    # Calculate stats for landing page
    total = Complaint.objects.count()
    resolved = Complaint.objects.filter(status__in=['resolved', 'closed']).count()
    pending = Complaint.objects.filter(status='pending').count()
    in_progress = Complaint.objects.filter(status='in_progress').count()

    context = {
        'total_complaints': total,
        'resolved_complaints': resolved,
        'pending_complaints': pending,
        'in_progress_complaints': in_progress,
    }
    return render(request, 'complaints/landing.html', context)

# Register View
def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = RegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Registration successful! Welcome to the Hostel Complaint Portal, {user.username}.")
            return redirect('dashboard')
        else:
            messages.error(request, "Registration failed. Please correct the errors below.")
    else:
        form = RegistrationForm()
    
    return render(request, 'complaints/register.html', {'form': form})

# Login View
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {username}!")
                return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    
    return render(request, 'complaints/login.html', {'form': form})

# Logout View
def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('landing')

# Unified Dashboard Route
@login_required
def dashboard(request):
    if is_warden(request.user):
        return redirect('warden_dashboard')
    return redirect('student_dashboard')

# Student Dashboard
@login_required
def student_dashboard(request):
    if is_warden(request.user):
        return redirect('warden_dashboard')

    # Get student's complaints
    complaints = Complaint.objects.filter(student=request.user)

    # Search & filters
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    category_filter = request.GET.get('category', '')

    if search_query:
        complaints = complaints.filter(
            Q(title__icontains=search_query) | Q(description__icontains=search_query)
        )
    if status_filter:
        complaints = complaints.filter(status=status_filter)
    if category_filter:
        complaints = complaints.filter(category=category_filter)

    # Calculate stats
    total = complaints.count()
    pending = complaints.filter(status='pending').count()
    in_progress = complaints.filter(status='in_progress').count()
    resolved = complaints.filter(status='resolved').count()
    closed = complaints.filter(status='closed').count()

    context = {
        'complaints': complaints,
        'total_count': total,
        'pending_count': pending,
        'in_progress_count': in_progress,
        'resolved_count': resolved,
        'closed_count': closed,
        'search_query': search_query,
        'status_filter': status_filter,
        'category_filter': category_filter,
    }
    return render(request, 'complaints/student_dashboard.html', context)

# Warden Dashboard
@login_required
@user_passes_test(is_warden, login_url='student_dashboard')
def warden_dashboard(request):
    # Handle Warden creating a new Hostel
    if request.method == 'POST' and request.POST.get('action_type') == 'create_hostel':
        hostel_form = HostelForm(request.POST)
        if hostel_form.is_valid():
            hostel = hostel_form.save(commit=False)
            hostel.warden = request.user
            hostel.code = generate_hostel_key()
            hostel.save()
            messages.success(request, f"Hostel '{hostel.name}' created successfully! Hostel Key: {hostel.code}")
            return redirect('warden_dashboard')
        else:
            messages.error(request, "Failed to create hostel. Check the input details.")
    else:
        hostel_form = HostelForm()

    # Get Warden's managed hostels
    warden_hostels = Hostel.objects.filter(warden=request.user)
    
    # Scoped Queryset Filtering for Multi-Hostel Security
    if warden_hostels.exists():
        base_complaints = Complaint.objects.filter(
            Q(hostel__in=warden_hostels) | Q(student__profile__hostel__in=warden_hostels)
        ).distinct()
    elif request.user.is_superuser:
        base_complaints = Complaint.objects.all()
    else:
        base_complaints = Complaint.objects.none()

    complaints = base_complaints

    # Filters applied on top of base queryset
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    category_filter = request.GET.get('category', '')
    priority_filter = request.GET.get('priority', '')
    block_filter = request.GET.get('block', '')

    if search_query:
        complaints = complaints.filter(
            Q(title__icontains=search_query) | 
            Q(description__icontains=search_query) |
            Q(student__username__icontains=search_query)
        )
    if status_filter:
        complaints = complaints.filter(status=status_filter)
    if category_filter:
        complaints = complaints.filter(category=category_filter)
    if priority_filter:
        complaints = complaints.filter(priority=priority_filter)
    if block_filter:
        complaints = complaints.filter(hostel_block__icontains=block_filter)

    # Scoped KPI calculations exclusively for warden's hostel
    total = base_complaints.count()
    pending = base_complaints.filter(status='pending').count()
    in_progress = base_complaints.filter(status='in_progress').count()
    resolved = base_complaints.filter(status='resolved').count()
    closed = base_complaints.filter(status='closed').count()

    # Scoped Chart Data
    category_data = base_complaints.values('category').annotate(count=Count('id'))
    category_labels = []
    category_counts = []
    from .models import CATEGORY_CHOICES
    cat_mapping = dict(CATEGORY_CHOICES)
    for entry in category_data:
        category_labels.append(cat_mapping.get(entry['category'], entry['category']))
        category_counts.append(entry['count'])

    status_data = base_complaints.values('status').annotate(count=Count('id'))
    status_labels = []
    status_counts = []
    from .models import STATUS_CHOICES
    status_mapping = dict(STATUS_CHOICES)
    for entry in status_data:
        status_labels.append(status_mapping.get(entry['status'], entry['status']))
        status_counts.append(entry['count'])

    blocks = base_complaints.values_list('hostel_block', flat=True).distinct()

    context = {
        'complaints': complaints,
        'total_count': total,
        'pending_count': pending,
        'in_progress_count': in_progress,
        'resolved_count': resolved,
        'closed_count': closed,
        
        'search_query': search_query,
        'status_filter': status_filter,
        'category_filter': category_filter,
        'priority_filter': priority_filter,
        'block_filter': block_filter,
        
        'blocks': blocks,
        'warden_hostels': warden_hostels,
        'hostel_form': hostel_form,
        'chart_categories_json': json.dumps(category_labels),
        'chart_category_counts_json': json.dumps(category_counts),
        'chart_statuses_json': json.dumps(status_labels),
        'chart_status_counts_json': json.dumps(status_counts),
    }
    return render(request, 'complaints/warden_dashboard.html', context)

# Submit Complaint (Student)
@login_required
def create_complaint(request):
    if is_warden(request.user):
        messages.error(request, "Wardens cannot file complaints.")
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = ComplaintForm(request.POST, request.FILES)
        if form.is_valid():
            complaint = form.save(commit=False)
            complaint.student = request.user
            complaint.status = 'pending'
            
            # Associate complaint with student's hostel
            if hasattr(request.user, 'profile') and request.user.profile.hostel:
                complaint.hostel = request.user.profile.hostel
                if not complaint.hostel_block:
                    complaint.hostel_block = request.user.profile.hostel.name
            
            complaint.save()
            messages.success(request, "Complaint submitted successfully! It is now pending warden review.")
            return redirect('dashboard')
        else:
            messages.error(request, "Failed to submit complaint. Check the form details.")
    else:
        # Prepopulate student room and block
        initial_data = {}
        if hasattr(request.user, 'profile'):
            initial_data = {
                'room_no': request.user.profile.room_no,
                'hostel_block': request.user.profile.hostel_block or (request.user.profile.hostel.name if request.user.profile.hostel else ''),
            }
        form = ComplaintForm(initial=initial_data)
        
    return render(request, 'complaints/create_complaint.html', {'form': form})

# Complaint Detail & Management Page
@login_required
def complaint_detail(request, pk):
    complaint = get_object_or_404(Complaint, pk=pk)
    
    # Check permissions
    if not is_warden(request.user) and complaint.student != request.user:
        messages.error(request, "You do not have permission to view this complaint.")
        return redirect('dashboard')
        
    # Get all related comments. If student, hide comments marked internal
    if is_warden(request.user):
        comments = complaint.comments.all()
    else:
        comments = complaint.comments.filter(is_internal=False)

    # Initialize forms
    action_form = None
    comment_form = CommentForm()
    feedback_form = None

    if is_warden(request.user):
        action_form = WardenComplaintActionForm(instance=complaint)
    elif complaint.status == 'resolved':
        feedback_form = FeedbackForm(instance=complaint)

    # Handle POST requests (actions, comments, or feedback)
    if request.method == 'POST':
        action_type = request.POST.get('action_type', '')

        # Action 1: Post comment
        if action_type == 'add_comment':
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.complaint = complaint
                comment.author = request.user
                
                if not is_warden(request.user):
                    comment.is_internal = False
                
                comment.save()
                messages.success(request, "Comment posted successfully.")
                return redirect('complaint_detail', pk=complaint.pk)
        
        # Action 2: Warden update complaint (Status, Priority, Assign Staff)
        elif action_type == 'update_complaint' and is_warden(request.user):
            old_status = complaint.status
            action_form = WardenComplaintActionForm(request.POST, instance=complaint)
            if action_form.is_valid():
                updated_complaint = action_form.save()
                
                # Check for status transition into Resolved to trigger email notification
                if old_status != 'resolved' and updated_complaint.status == 'resolved':
                    send_resolution_email(updated_complaint)
                    
                messages.success(request, f"Complaint details updated. Status set to: {updated_complaint.get_status_display()}")
                return redirect('complaint_detail', pk=complaint.pk)
        
        # Action 3: Student feedback / rating submission
        elif action_type == 'submit_feedback' and complaint.student == request.user and complaint.status == 'resolved':
            feedback_form = FeedbackForm(request.POST, instance=complaint)
            if feedback_form.is_valid():
                obj = feedback_form.save(commit=False)
                obj.status = 'closed'  # Mark the complaint closed upon receiving feedback
                obj.save()
                messages.success(request, "Feedback submitted. Complaint marked as Closed.")
                return redirect('complaint_detail', pk=complaint.pk)

    context = {
        'complaint': complaint,
        'comments': comments,
        'action_form': action_form,
        'comment_form': comment_form,
        'feedback_form': feedback_form,
        'is_warden': is_warden(request.user),
    }
    return render(request, 'complaints/complaint_detail.html', context)

# Reopen Complaint (Student)
@login_required
def reopen_complaint(request, pk):
    complaint = get_object_or_404(Complaint, pk=pk)
    
    # Permissions
    if complaint.student != request.user:
        messages.error(request, "You cannot modify this complaint.")
        return redirect('dashboard')
        
    if complaint.status in ['resolved', 'closed']:
        complaint.status = 'in_progress'
        complaint.rating = None
        complaint.feedback = ""
        complaint.save()
        
        # Create auto-comment explaining reopen
        Comment.objects.create(
            complaint=complaint,
            author=request.user,
            message="[System Notification] Student reopened this complaint because the resolution was unsatisfactory.",
            is_internal=False
        )
        messages.warning(request, "Complaint reopened and status set back to In Progress.")
        return redirect('complaint_detail', pk=complaint.pk)
    else:
        messages.error(request, "This complaint is not currently resolved or closed.")
        return redirect('complaint_detail', pk=complaint.pk)


from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile, Complaint, Comment, Hostel, CATEGORY_CHOICES, PRIORITY_CHOICES, STATUS_CHOICES, ROLE_CHOICES

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(choices=ROLE_CHOICES, required=True, initial='student')
    hostel_key = forms.CharField(max_length=20, required=False, label="Hostel Key (Required for Students)", widget=forms.TextInput(attrs={'placeholder': 'E.g., ABC7X92K'}))
    roll_no = forms.CharField(max_length=20, required=False, label="Roll Number (Students Only)")
    room_no = forms.CharField(max_length=10, required=False, label="Room Number (Students Only)")
    hostel_block = forms.CharField(max_length=30, required=False, label="Hostel Block/Name (Optional if Key provided)")
    phone = forms.CharField(max_length=15, required=False, label="Phone Number")
    avatar = forms.ImageField(required=False, label="Profile Picture")

    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + ('email',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
        
        # Add special design classes for file input
        self.fields['avatar'].widget.attrs.update({'class': 'form-control-file'})

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        roll_no = cleaned_data.get('roll_no')
        room_no = cleaned_data.get('room_no')
        hostel_key = cleaned_data.get('hostel_key', '').strip()

        if role == 'student':
            if not roll_no:
                self.add_error('roll_no', 'Roll number is required for students.')
            if not room_no:
                self.add_error('room_no', 'Room number is required for students.')
            
            if not hostel_key:
                self.add_error('hostel_key', 'Invalid Hostel Key. Please enter the correct key provided by your hostel warden.')
            else:
                hostel_obj = Hostel.objects.filter(code__iexact=hostel_key).first()
                if not hostel_obj:
                    self.add_error('hostel_key', 'Invalid Hostel Key. Please enter the correct key provided by your hostel warden.')
                else:
                    cleaned_data['hostel_obj'] = hostel_obj
        
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            profile = user.profile
            profile.role = self.cleaned_data.get('role')
            profile.roll_no = self.cleaned_data.get('roll_no', '')
            profile.room_no = self.cleaned_data.get('room_no', '')
            profile.phone = self.cleaned_data.get('phone', '')
            
            hostel_obj = self.cleaned_data.get('hostel_obj')
            if hostel_obj:
                profile.hostel = hostel_obj
                profile.hostel_block = hostel_obj.name
            else:
                profile.hostel_block = self.cleaned_data.get('hostel_block', '')
                
            if self.cleaned_data.get('avatar'):
                profile.avatar = self.cleaned_data.get('avatar')
            profile.save()
        return user

class HostelForm(forms.ModelForm):
    class Meta:
        model = Hostel
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'E.g., ABC Boys Hostel, Narmada Hostel', 'class': 'form-control'}),
        }


class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ['title', 'category', 'priority', 'description', 'room_no', 'hostel_block', 'attachment']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'E.g., Fan not working, water leakage in bathroom'}),
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Provide detailed explanation of the issue...'}),
            'room_no': forms.TextInput(attrs={'placeholder': 'E.g., 204-A'}),
            'hostel_block': forms.TextInput(attrs={'placeholder': 'E.g., Block B, Narmada Hostel'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
        self.fields['category'].widget.attrs.update({'class': 'form-select'})
        self.fields['priority'].widget.attrs.update({'class': 'form-select'})

class WardenComplaintActionForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ['status', 'assigned_staff', 'priority']
        widgets = {
            'assigned_staff': forms.TextInput(attrs={'placeholder': 'Enter technician/staff name'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
        self.fields['status'].widget.attrs.update({'class': 'form-select'})
        self.fields['priority'].widget.attrs.update({'class': 'form-select'})

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['message', 'is_internal']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Type your message/comment here...', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        # We might hide/show is_internal depending on user role in views, but define it here
        super().__init__(*args, **kwargs)
        self.fields['message'].widget.attrs.update({'class': 'form-control'})
        self.fields['is_internal'].widget.attrs.update({'class': 'form-check-input'})

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ['rating', 'feedback']
        widgets = {
            'rating': forms.Select(choices=[(i, f"{i} Stars" if i > 1 else "1 Star") for i in range(1, 6)], attrs={'class': 'form-select'}),
            'feedback': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Add feedback details or experience (optional)...', 'class': 'form-control'}),
        }

from django.contrib import admin
from .models import Profile, Complaint, Comment, Hostel

@admin.register(Hostel)
class HostelAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'warden', 'created_at')
    search_fields = ('name', 'code', 'warden__username')
    list_filter = ('created_at',)

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'hostel', 'roll_no', 'room_no', 'hostel_block', 'phone')
    list_filter = ('role', 'hostel', 'hostel_block')
    search_fields = ('user__username', 'user__email', 'roll_no', 'phone', 'hostel__name')

@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'student', 'hostel', 'category', 'priority', 'status', 'assigned_staff', 'created_at')
    list_filter = ('status', 'priority', 'category', 'hostel', 'hostel_block')
    search_fields = ('title', 'description', 'student__username', 'room_no', 'assigned_staff', 'hostel__name')
    date_hierarchy = 'created_at'

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('complaint', 'author', 'created_at', 'is_internal')
    list_filter = ('is_internal', 'created_at')
    search_fields = ('message', 'author__username')


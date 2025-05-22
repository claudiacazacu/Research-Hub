from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Profile, Project, ProjectMember, Objective, Activity, Notification
)

# Profile Admin
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'institution', 'position', 'phone')
    list_filter = ('role', 'institution')
    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name', 'institution')
    raw_id_fields = ('user',)

# ProjectMember Inline for Project
class ProjectMemberInline(admin.TabularInline):
    model = ProjectMember
    extra = 1
    raw_id_fields = ('user',)

# Objective Inline for Project
class ObjectiveInline(admin.TabularInline):
    model = Objective
    extra = 1

# Project Admin
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'start_date', 'end_date', 'created_by', 'created_at', 'progress_display')
    list_filter = ('status', 'start_date', 'end_date')
    search_fields = ('title', 'description', 'created_by__username')
    date_hierarchy = 'created_at'
    inlines = [ProjectMemberInline, ObjectiveInline]
    raw_id_fields = ('created_by',)
    
    def progress_display(self, obj):
        progress = obj.progress_percentage()
        color = 'green' if progress >= 75 else 'orange' if progress >= 25 else 'red'
        return format_html(
            '<div style="width:100px; background-color: #f1f1f1; border-radius: 4px;">'
            '<div style="width: {}%; background-color: {}; height: 10px; border-radius: 4px;"></div>'
            '</div> {}%',
            progress, color, progress
        )
    progress_display.short_description = 'Progres'

# Activity Admin
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('title', 'project', 'objective', 'status', 'start_date', 'due_date', 'assigned_to')
    list_filter = ('status', 'due_date', 'project')
    search_fields = ('title', 'description', 'project__title')
    raw_id_fields = ('project', 'objective', 'assigned_to')
    date_hierarchy = 'due_date'

# Notification Admin
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'notification_type', 'created_at', 'read')
    list_filter = ('notification_type', 'read', 'created_at')
    search_fields = ('title', 'message', 'user__username')
    raw_id_fields = ('user', 'related_project', 'related_activity')
    date_hierarchy = 'created_at'

# Register all models
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(Activity, ActivityAdmin)
admin.site.register(Notification, NotificationAdmin)

# Customize admin site header and title
admin.site.site_header = 'Platforma de Cercetare - Administrare'
admin.site.site_title = 'Administrare Platforma'
admin.site.index_title = 'Panou de administrare'
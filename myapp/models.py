from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Profile(models.Model):
    """Extinderea modelului de User standard cu informații suplimentare."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    picture = models.ImageField(upload_to='profile_pics', blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True)
    institution = models.CharField(max_length=100, blank=True)
    position = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('researcher', 'Cercetător'),
        ('coordinator', 'Coordonator'),
        ('evaluator', 'Evaluator'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='researcher')
    
    def __str__(self):
        return f'{self.user.username} Profile'


class Project(models.Model):
    """Model principal pentru proiecte de cercetare."""
    title = models.CharField(max_length=200)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_projects')
    
    STATUS_CHOICES = [
        ('draft', 'Schiță'),
        ('planning', 'Planificare'),
        ('in_progress', 'În desfășurare'),
        ('on_hold', 'Suspendat'),
        ('completed', 'Finalizat'),
        ('archived', 'Arhivat'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    def __str__(self):
        return self.title
    
    def progress_percentage(self):
        """Calculează procentul de progres al proiectului bazat pe activitățile completate."""
        total_activities = self.activities.count()
        if total_activities == 0:
            return 0
        completed_activities = self.activities.filter(status='completed').count()
        return int((completed_activities / total_activities) * 100)
    
    def days_remaining(self):
        """Returnează numărul de zile până la termenul limită al proiectului."""
        return (self.end_date - timezone.now().date()).days
    
    def is_overdue(self):
        """Verifică dacă proiectul a depășit termenul limită."""
        return self.end_date < timezone.now().date() and self.status not in ['completed', 'archived']


class ProjectMember(models.Model):
    """Legătura dintre utilizatori și proiecte, cu roluri în cadrul proiectului."""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='project_memberships')
    joined_at = models.DateTimeField(auto_now_add=True)
    
    ROLE_CHOICES = [
        ('leader', 'Lider de proiect'),
        ('researcher', 'Cercetător'),
        ('assistant', 'Asistent'),
        ('consultant', 'Consultant'),
        ('admin', 'Administrator'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='researcher')
    
    class Meta:
        unique_together = ('project', 'user')
    
    def __str__(self):
        return f'{self.user.username} - {self.project.title} ({self.get_role_display()})'


class Objective(models.Model):
    """Obiectivele proiectului."""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='objectives')
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title
    
    def progress_percentage(self):
        """Calculează procentul de progres al obiectivului bazat pe activitățile completate."""
        total_activities = self.activities.count()
        if total_activities == 0:
            return 0
        completed_activities = self.activities.filter(status='completed').count()
        return int((completed_activities / total_activities) * 100)


class Activity(models.Model):
    """Activități individuale asociate proiectelor sau obiectivelor."""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='activities')
    objective = models.ForeignKey(Objective, on_delete=models.SET_NULL, related_name='activities', null=True, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    start_date = models.DateField()
    due_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='assigned_activities', null=True, blank=True)
    
    STATUS_CHOICES = [
        ('not_started', 'Neîncepută'),
        ('in_progress', 'În desfășurare'),
        ('review', 'În revizuire'),
        ('completed', 'Finalizată'),
        ('delayed', 'Întârziată'),
        ('cancelled', 'Anulată'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_started')
    
    def __str__(self):
        return self.title
    
    def is_overdue(self):
        """Verifică dacă activitatea a depășit termenul limită."""
        return self.due_date < timezone.now().date() and self.status not in ['completed', 'cancelled']


class Notification(models.Model):
    """Notificări pentru utilizatori."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    
    TYPE_CHOICES = [
        ('deadline', 'Deadline apropiat'),
        ('activity', 'Activitate nouă'),
        ('team', 'Modificare echipă'),
        ('system', 'Mesaj sistem'),
    ]
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='system')
    
    related_project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    related_activity = models.ForeignKey(Activity, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-created_at']
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .forms import CustomAuthenticationForm

urlpatterns = [
    # Pagina principală
    path('', views.home, name='home'),
    
    # Autentificare și profil
    path('login/', auth_views.LoginView.as_view(
        template_name='auth/login.html',
        authentication_form=CustomAuthenticationForm
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    
    # Proiecte
    path('projects/', views.projects_list, name='projects_list'),
    path('projects/create/', views.create_project, name='create_project'),
    path('projects/<int:project_id>/', views.project_detail, name='project_detail'),
    path('projects/<int:project_id>/edit/', views.edit_project, name='edit_project'),
    path('projects/<int:project_id>/delete/', views.delete_project, name='delete_project'),
    
    # Membri proiect
    path('projects/<int:project_id>/members/', views.project_members, name='project_members'),
    path('projects/<int:project_id>/members/add/', views.add_project_member, name='add_project_member'),
    path('projects/<int:project_id>/members/<int:member_id>/remove/', views.remove_project_member, name='remove_project_member'),
    
    # Obiective
    path('projects/<int:project_id>/objectives/create/', views.create_objective, name='create_objective'),
    path('objectives/<int:objective_id>/edit/', views.edit_objective, name='edit_objective'),
    path('objectives/<int:objective_id>/delete/', views.delete_objective, name='delete_objective'),
    
    # Activități
    path('projects/<int:project_id>/activities/create/', views.create_activity, name='create_activity'),
    path('activities/<int:activity_id>/edit/', views.edit_activity, name='edit_activity'),
    path('activities/<int:activity_id>/delete/', views.delete_activity, name='delete_activity'),
    path('activities/<int:activity_id>/status/', views.change_activity_status, name='change_activity_status'),
    
    # Notificări
    path('notifications/', views.notifications_list, name='notifications_list'),
    path('notifications/<int:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/mark-all-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
    
    # Echipe (temporar)
    path('teams/', views.teams_list, name='teams_list'),
    path('teams/<int:project_id>/', views.team_detail, name='team_detail'),
    
    # Task-uri (temporar)
    path('tasks/', views.my_tasks, name='my_tasks'),
    path('tasks/all/', views.all_tasks, name='all_tasks'),
    path('tasks/create/', views.create_task, name='create_task'),
    path('tasks/<int:task_id>/', views.task_detail, name='task_detail'),
]
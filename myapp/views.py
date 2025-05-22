from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Q, Count
from django.core.paginator import Paginator
from .models import (
    Project, ProjectMember, Objective, Activity, Notification, Profile
)
from .forms import (
    CustomUserCreationForm, ProfileForm, ProjectForm,
    ObjectiveForm, ActivityForm
)

def home(request):
    """Pagina principală a aplicației."""
    # Dacă utilizatorul este autentificat, încercăm să afișăm informații relevante
    context = {}
    
    if request.user.is_authenticated:
        try:
            # Obținem proiectele în care utilizatorul este membru
            user_projects = ProjectMember.objects.filter(
                user=request.user
            ).select_related('project').order_by('-project__updated_at')[:3]
            
            # Obținem activitățile apropiate ale utilizatorului
            upcoming_activities = Activity.objects.filter(
                assigned_to=request.user,
                due_date__gte=timezone.now().date(),
                status__in=['not_started', 'in_progress']
            ).select_related('project').order_by('due_date')[:3]
            
            # Obținem notificările necitite
            unread_notifications = Notification.objects.filter(
                user=request.user,
                read=False
            ).order_by('-created_at')[:5]
            
            context.update({
                'user_projects': user_projects,
                'upcoming_activities': upcoming_activities,
                'unread_notifications': unread_notifications,
            })
        except Exception as e:
            # În cazul în care apar erori, continuăm fără aceste date
            messages.error(request, f"A apărut o eroare: {str(e)}")
    
    return render(request, 'home.html', context)

def register(request):
    """Înregistrarea unui utilizator nou."""
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Autentificăm automat utilizatorul după înregistrare
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=user.username, password=raw_password)
            login(request, user)
            messages.success(request, "Contul a fost creat cu succes și ești acum autentificat.")
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'auth/register.html', {'form': form})

@login_required
def profile(request):
    """Afișează și editează profilul utilizatorului."""
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        # Dacă nu există, creăm un profil pentru utilizator
        profile = Profile(user=request.user)
        profile.save()
    
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profilul a fost actualizat cu succes.")
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile)
    
    # Obținem statistici pentru profilul utilizatorului
    active_projects = ProjectMember.objects.filter(
        user=request.user,
        project__status__in=['planning', 'in_progress']
    ).count()
    
    completed_activities = Activity.objects.filter(
        assigned_to=request.user,
        status='completed'
    ).count()
    
    # Obținem proiectele utilizatorului
    user_projects = ProjectMember.objects.filter(
        user=request.user
    ).select_related('project').order_by('-project__updated_at')[:5]
    
    # Obținem activitățile apropiate
    upcoming_activities = Activity.objects.filter(
        assigned_to=request.user, 
        due_date__gte=timezone.now().date()
    ).select_related('project').order_by('due_date')[:5]
    
    context = {
        'form': form,
        'active_projects': active_projects,
        'completed_activities': completed_activities,
        'user_projects': user_projects,
        'upcoming_activities': upcoming_activities,
    }
    
    return render(request, 'profile.html', context)

@login_required
def projects_list(request):
    """Afișează lista tuturor proiectelor utilizatorului."""
    # Obținem proiectele în care utilizatorul este membru
    user_projects = ProjectMember.objects.filter(
        user=request.user
    ).select_related('project')
    
    # Aplicăm filtre dacă există
    status_filter = request.GET.get('status')
    if status_filter:
        user_projects = user_projects.filter(project__status=status_filter)
    
    search_query = request.GET.get('search')
    if search_query:
        user_projects = user_projects.filter(
            Q(project__title__icontains=search_query) | 
            Q(project__description__icontains=search_query)
        )
    
    # Sortăm proiectele
    sort_by = request.GET.get('sort', '-project__updated_at')
    user_projects = user_projects.order_by(sort_by)
    
    # Paginare
    paginator = Paginator(user_projects, 10)  # 10 proiecte per pagină
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Obținem toate statusurile posibile pentru filtrare
    all_statuses = [status[0] for status in Project.STATUS_CHOICES]
    
    context = {
        'page_obj': page_obj,
        'all_statuses': all_statuses,
        'current_status': status_filter,
        'search_query': search_query,
        'current_sort': sort_by,
    }
    
    return render(request, 'projects/list.html', context)

@login_required
def project_detail(request, project_id):
    """Afișează detaliile unui proiect specific."""
    # Obținem proiectul și verificăm dacă utilizatorul are acces
    project = get_object_or_404(Project, id=project_id)
    
    # Verificăm dacă utilizatorul este membru al proiectului
    if not ProjectMember.objects.filter(project=project, user=request.user).exists():
        messages.error(request, "Nu aveți acces la acest proiect.")
        return redirect('projects_list')
    
    # Obținem informații despre membri
    members = ProjectMember.objects.filter(project=project).select_related('user')
    
    # Obținem obiectivele proiectului
    objectives = Objective.objects.filter(project=project)
    
    # Obținem activitățile proiectului
    activities = Activity.objects.filter(project=project).order_by('due_date')
    
    # Calculăm progresul proiectului
    progress = project.progress_percentage()
    
    context = {
        'project': project,
        'members': members,
        'objectives': objectives,
        'activities': activities,
        'progress': progress,
    }
    
    return render(request, 'projects/detail.html', context)

@login_required
def create_project(request):
    """Creează un proiect nou."""
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            # Salvăm proiectul
            project = form.save(commit=False)
            project.created_by = request.user
            project.save()
            
            # Adăugăm utilizatorul curent ca lider al proiectului
            ProjectMember.objects.create(
                project=project,
                user=request.user,
                role='leader'
            )
            
            messages.success(request, f"Proiectul '{project.title}' a fost creat cu succes.")
            return redirect('project_detail', project_id=project.id)
    else:
        form = ProjectForm()
    
    return render(request, 'projects/create.html', {'form': form})

@login_required
def edit_project(request, project_id):
    """Editează un proiect existent."""
    project = get_object_or_404(Project, id=project_id)
    
    # Verificăm dacă utilizatorul are permisiunea să editeze proiectul
    member = ProjectMember.objects.filter(project=project, user=request.user).first()
    if not member or member.role not in ['leader', 'admin']:
        messages.error(request, "Nu aveți permisiunea de a edita acest proiect.")
        return redirect('project_detail', project_id=project.id)
    
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, f"Proiectul '{project.title}' a fost actualizat cu succes.")
            return redirect('project_detail', project_id=project.id)
    else:
        form = ProjectForm(instance=project)
    
    return render(request, 'projects/edit.html', {'form': form, 'project': project})

@login_required
def delete_project(request, project_id):
    """Șterge un proiect."""
    project = get_object_or_404(Project, id=project_id)
    
    # Verificăm dacă utilizatorul are permisiunea să șteargă proiectul
    member = ProjectMember.objects.filter(project=project, user=request.user).first()
    if not member or member.role not in ['leader', 'admin']:
        messages.error(request, "Nu aveți permisiunea de a șterge acest proiect.")
        return redirect('project_detail', project_id=project.id)
    
    if request.method == 'POST':
        project_title = project.title
        project.delete()
        messages.success(request, f"Proiectul '{project_title}' a fost șters cu succes.")
        return redirect('projects_list')
    
    return render(request, 'projects/delete.html', {'project': project})

@login_required
def project_members(request, project_id):
    """Gestionează membrii unui proiect."""
    project = get_object_or_404(Project, id=project_id)
    
    # Verificăm dacă utilizatorul are permisiunea să gestioneze membrii
    member = ProjectMember.objects.filter(project=project, user=request.user).first()
    if not member or member.role not in ['leader', 'admin']:
        messages.error(request, "Nu aveți permisiunea de a gestiona membrii acestui proiect.")
        return redirect('project_detail', project_id=project.id)
    
    # Obținem membrii actuali ai proiectului
    project_members = ProjectMember.objects.filter(project=project).select_related('user')
    
    context = {
        'project': project,
        'project_members': project_members,
    }
    
    return render(request, 'projects/members.html', context)

@login_required
def add_project_member(request, project_id):
    """Adaugă un membru la un proiect."""
    project = get_object_or_404(Project, id=project_id)
    
    # Verificăm dacă utilizatorul are permisiunea să adauge membri
    member = ProjectMember.objects.filter(project=project, user=request.user).first()
    if not member or member.role not in ['leader', 'admin']:
        messages.error(request, "Nu aveți permisiunea de a adăuga membri la acest proiect.")
        return redirect('project_members', project_id=project.id)
    
    if request.method == 'POST':
        # Obținem utilizatorul și rolul din formular
        user_id = request.POST.get('user_id')
        role = request.POST.get('role')
        
        if user_id and role:
            try:
                user = User.objects.get(id=user_id)
                # Verificăm dacă utilizatorul nu este deja membru
                if not ProjectMember.objects.filter(project=project, user=user).exists():
                    ProjectMember.objects.create(
                        project=project,
                        user=user,
                        role=role
                    )
                    messages.success(request, f"{user.username} a fost adăugat la proiect ca {dict(ProjectMember.ROLE_CHOICES)[role]}.")
                else:
                    messages.warning(request, f"{user.username} este deja membru al proiectului.")
            except User.DoesNotExist:
                messages.error(request, "Utilizatorul specificat nu există.")
        else:
            messages.error(request, "Trebuie să specificați un utilizator și un rol.")
        
        return redirect('project_members', project_id=project.id)
    
    # Obținem toți utilizatorii care nu sunt deja membri ai proiectului
    existing_member_ids = ProjectMember.objects.filter(project=project).values_list('user_id', flat=True)
    available_users = User.objects.exclude(id__in=existing_member_ids)
    
    context = {
        'project': project,
        'available_users': available_users,
        'role_choices': ProjectMember.ROLE_CHOICES,
    }
    
    return render(request, 'projects/add_member.html', context)

@login_required
def remove_project_member(request, project_id, member_id):
    """Elimină un membru dintr-un proiect."""
    project = get_object_or_404(Project, id=project_id)
    project_member = get_object_or_404(ProjectMember, id=member_id, project=project)
    
    # Verificăm dacă utilizatorul are permisiunea să elimine membri
    member = ProjectMember.objects.filter(project=project, user=request.user).first()
    if not member or member.role not in ['leader', 'admin']:
        messages.error(request, "Nu aveți permisiunea de a elimina membri din acest proiect.")
        return redirect('project_members', project_id=project.id)
    
    # Nu permitem eliminarea liderului de proiect dacă este singurul lider
    if project_member.role == 'leader' and ProjectMember.objects.filter(project=project, role='leader').count() <= 1:
        messages.error(request, "Nu puteți elimina singurul lider al proiectului.")
        return redirect('project_members', project_id=project.id)
    
    # Nu permitem eliminarea propriului cont
    if project_member.user == request.user:
        messages.error(request, "Nu vă puteți elimina din proiect. Contactați alt lider de proiect.")
        return redirect('project_members', project_id=project.id)
    
    if request.method == 'POST':
        # Eliminăm membrul
        username = project_member.user.username
        project_member.delete()
        messages.success(request, f"{username} a fost eliminat din proiect.")
        return redirect('project_members', project_id=project.id)
    
    return render(request, 'projects/remove_member.html', {'project': project, 'member': project_member})

@login_required
def create_objective(request, project_id):
    """Creează un obiectiv nou pentru un proiect."""
    project = get_object_or_404(Project, id=project_id)
    
    # Verificăm dacă utilizatorul are permisiunea să adauge obiective
    member = ProjectMember.objects.filter(project=project, user=request.user).first()
    if not member or member.role not in ['leader', 'admin', 'researcher']:
        messages.error(request, "Nu aveți permisiunea de a adăuga obiective la acest proiect.")
        return redirect('project_detail', project_id=project.id)
    
    if request.method == 'POST':
        form = ObjectiveForm(request.POST)
        if form.is_valid():
            objective = form.save(commit=False)
            objective.project = project
            objective.save()
            messages.success(request, f"Obiectivul '{objective.title}' a fost adăugat cu succes.")
            return redirect('project_detail', project_id=project.id)
    else:
        form = ObjectiveForm()
    
    return render(request, 'projects/create_objective.html', {'form': form, 'project': project})

@login_required
def edit_objective(request, objective_id):
    """Editează un obiectiv existent."""
    objective = get_object_or_404(Objective, id=objective_id)
    project = objective.project
    
    # Verificăm dacă utilizatorul are permisiunea să editeze obiective
    member = ProjectMember.objects.filter(project=project, user=request.user).first()
    if not member or member.role not in ['leader', 'admin', 'researcher']:
        messages.error(request, "Nu aveți permisiunea de a edita acest obiectiv.")
        return redirect('project_detail', project_id=project.id)
    
    if request.method == 'POST':
        form = ObjectiveForm(request.POST, instance=objective)
        if form.is_valid():
            form.save()
            messages.success(request, f"Obiectivul '{objective.title}' a fost actualizat cu succes.")
            return redirect('project_detail', project_id=project.id)
    else:
        form = ObjectiveForm(instance=objective)
    
    return render(request, 'projects/edit_objective.html', {'form': form, 'objective': objective, 'project': project})

@login_required
def delete_objective(request, objective_id):
    """Șterge un obiectiv."""
    objective = get_object_or_404(Objective, id=objective_id)
    project = objective.project
    
    # Verificăm dacă utilizatorul are permisiunea să șteargă obiective
    member = ProjectMember.objects.filter(project=project, user=request.user).first()
    if not member or member.role not in ['leader', 'admin']:
        messages.error(request, "Nu aveți permisiunea de a șterge acest obiectiv.")
        return redirect('project_detail', project_id=project.id)
    
    if request.method == 'POST':
        objective_title = objective.title
        objective.delete()
        messages.success(request, f"Obiectivul '{objective_title}' a fost șters cu succes.")
        return redirect('project_detail', project_id=project.id)
    
    return render(request, 'projects/delete_objective.html', {'objective': objective, 'project': project})

@login_required
def create_activity(request, project_id):
    """Creează o activitate nouă pentru un proiect."""
    project = get_object_or_404(Project, id=project_id)
    
    # Verificăm dacă utilizatorul are permisiunea să adauge activități
    member = ProjectMember.objects.filter(project=project, user=request.user).first()
    if not member:
        messages.error(request, "Nu aveți acces la acest proiect.")
        return redirect('projects_list')
    
    if request.method == 'POST':
        form = ActivityForm(project, request.POST)
        if form.is_valid():
            activity = form.save(commit=False)
            activity.project = project
            activity.save()
            
            # Creăm notificare pentru utilizatorul asignat
            if activity.assigned_to:
                Notification.objects.create(
                    user=activity.assigned_to,
                    title=f"Activitate nouă: {activity.title}",
                    message=f"Ai fost asignat la o nouă activitate în proiectul '{project.title}'.",
                    notification_type='activity',
                    related_project=project,
                    related_activity=activity
                )
            
            messages.success(request, f"Activitatea '{activity.title}' a fost creată cu succes.")
            return redirect('project_detail', project_id=project.id)
    else:
        form = ActivityForm(project)
    
    return render(request, 'projects/create_activity.html', {'form': form, 'project': project})

@login_required
def edit_activity(request, activity_id):
    """Editează o activitate existentă."""
    activity = get_object_or_404(Activity, id=activity_id)
    project = activity.project
    
    # Verificăm dacă utilizatorul are permisiunea să editeze activitatea
    member = ProjectMember.objects.filter(project=project, user=request.user).first()
    if not member:
        messages.error(request, "Nu aveți acces la acest proiect.")
        return redirect('projects_list')
    
    # Doar membrii cu roluri superioare sau utilizatorul asignat poate edita activitatea
    if member.role not in ['leader', 'admin', 'researcher'] and activity.assigned_to != request.user:
        messages.error(request, "Nu aveți permisiunea de a edita această activitate.")
        return redirect('project_detail', project_id=project.id)
    
    if request.method == 'POST':
        form = ActivityForm(project, request.POST, instance=activity)
        if form.is_valid():
            # Salvăm și creăm notificare dacă s-a schimbat persoana asignată
            old_assigned = activity.assigned_to
            updated_activity = form.save()
            
            if updated_activity.assigned_to and updated_activity.assigned_to != old_assigned:
                Notification.objects.create(
                    user=updated_activity.assigned_to,
                    title=f"Activitate atribuită: {updated_activity.title}",
                    message=f"Ai fost asignat la o activitate în proiectul '{project.title}'.",
                    notification_type='activity',
                    related_project=project,
                    related_activity=updated_activity
                )
            
            messages.success(request, f"Activitatea '{activity.title}' a fost actualizată cu succes.")
            return redirect('project_detail', project_id=project.id)
    else:
        form = ActivityForm(project, instance=activity)
    
    return render(request, 'projects/edit_activity.html', {'form': form, 'activity': activity, 'project': project})

@login_required
def delete_activity(request, activity_id):
    """Șterge o activitate."""
    activity = get_object_or_404(Activity, id=activity_id)
    project = activity.project
    
    # Verificăm dacă utilizatorul are permisiunea să șteargă activitatea
    member = ProjectMember.objects.filter(project=project, user=request.user).first()
    if not member or member.role not in ['leader', 'admin']:
        messages.error(request, "Nu aveți permisiunea de a șterge această activitate.")
        return redirect('project_detail', project_id=project.id)
    
    if request.method == 'POST':
        activity_title = activity.title
        activity.delete()
        messages.success(request, f"Activitatea '{activity_title}' a fost ștearsă cu succes.")
        return redirect('project_detail', project_id=project.id)
    
    return render(request, 'projects/delete_activity.html', {'activity': activity, 'project': project})

@login_required
def change_activity_status(request, activity_id):
    """Schimbă statusul unei activități."""
    activity = get_object_or_404(Activity, id=activity_id)
    project = activity.project
    
    # Verificăm dacă utilizatorul are permisiunea să modifice statusul
    member = ProjectMember.objects.filter(project=project, user=request.user).first()
    if not member:
        messages.error(request, "Nu aveți acces la acest proiect.")
        return redirect('projects_list')
    
    # Doar membrii cu roluri superioare sau utilizatorul asignat poate modifica statusul
    if member.role not in ['leader', 'admin', 'researcher'] and activity.assigned_to != request.user:
        messages.error(request, "Nu aveți permisiunea de a modifica statusul acestei activități.")
        return redirect('project_detail', project_id=project.id)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Activity.STATUS_CHOICES):
            old_status = activity.status
            activity.status = new_status
            activity.save()
            
            # Creăm notificare pentru liderul de proiect dacă activitatea a fost finalizată
            if new_status == 'completed' and old_status != 'completed':
                project_leaders = User.objects.filter(
                    project_memberships__project=project,
                    project_memberships__role='leader'
                )
                for leader in project_leaders:
                    Notification.objects.create(
                        user=leader,
                        title=f"Activitate finalizată: {activity.title}",
                        message=f"{request.user.get_full_name() or request.user.username} a finalizat activitatea '{activity.title}' în proiectul '{project.title}'.",
                        notification_type='activity',
                        related_project=project,
                        related_activity=activity
                    )
            
            messages.success(request, f"Statusul activității a fost schimbat în '{dict(Activity.STATUS_CHOICES)[new_status]}'.")
        else:
            messages.error(request, "Status invalid.")
        
        # Determinăm URL-ul de redirecționare (poate fi din profilul utilizatorului sau din detaliile proiectului)
        redirect_url = request.POST.get('redirect_url', 'project_detail')
        if redirect_url == 'profile':
            return redirect('profile')
        elif redirect_url == 'my_tasks':
            return redirect('my_tasks')
        else:
            return redirect('project_detail', project_id=project.id)
    
    return redirect('project_detail', project_id=project.id)

@login_required
def notifications_list(request):
    """Afișează lista notificărilor utilizatorului."""
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    
    # Paginare
    paginator = Paginator(notifications, 15)  # 15 notificări per pagină
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'notifications/list.html', {'page_obj': page_obj})

@login_required
def mark_notification_read(request, notification_id):
    """Marchează o notificare ca citită."""
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.read = True
    notification.save()
    
    # Verificăm dacă există un URL pentru redirecționare (de exemplu, către proiect sau activitate)
    if notification.related_activity:
        return redirect('project_detail', project_id=notification.related_project.id)
    elif notification.related_project:
        return redirect('project_detail', project_id=notification.related_project.id)
    else:
        return redirect('notifications_list')

@login_required
def mark_all_notifications_read(request):
    """Marchează toate notificările ca citite."""
    Notification.objects.filter(user=request.user).update(read=True)
    messages.success(request, "Toate notificările au fost marcate ca citite.")
    return redirect('notifications_list')

# View-uri complete pentru echipe și task-uri
@login_required
def teams_list(request):
    """Afișează lista echipelor în care utilizatorul este membru."""
    # Obținem toate proiectele în care utilizatorul este membru
    user_projects = ProjectMember.objects.filter(
        user=request.user
    ).select_related('project').order_by('-project__updated_at')
    
    # Aplicăm filtre dacă există
    search_query = request.GET.get('search')
    if search_query:
        user_projects = user_projects.filter(
            Q(project__title__icontains=search_query) | 
            Q(project__description__icontains=search_query)
        )
    
    # Paginare
    paginator = Paginator(user_projects, 12)  # 12 echipe per pagină
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
    }
    
    return render(request, 'teams/list.html', context)

@login_required
def team_detail(request, project_id):
    """Afișează detaliile unei echipe (proiect)."""
    project = get_object_or_404(Project, id=project_id)
    
    # Verificăm dacă utilizatorul este membru al proiectului
    if not ProjectMember.objects.filter(project=project, user=request.user).exists():
        messages.error(request, "Nu aveți acces la această echipă.")
        return redirect('teams_list')
    
    # Obținem membrii echipei
    members = ProjectMember.objects.filter(project=project).select_related('user__profile')
    
    # Obținem activitățile recente ale echipei
    recent_activities = Activity.objects.filter(
        project=project
    ).select_related('assigned_to').order_by('-updated_at')[:10]
    
    # Statistici echipă
    total_activities = Activity.objects.filter(project=project).count()
    completed_activities = Activity.objects.filter(project=project, status='completed').count()
    overdue_activities = Activity.objects.filter(
        project=project, 
        due_date__lt=timezone.now().date(),
        status__in=['not_started', 'in_progress']
    ).count()
    
    context = {
        'project': project,
        'members': members,
        'recent_activities': recent_activities,
        'total_activities': total_activities,
        'completed_activities': completed_activities,
        'overdue_activities': overdue_activities,
    }
    
    return render(request, 'teams/detail.html', context)

@login_required
def my_tasks(request):
    """Afișează toate task-urile (activitățile) utilizatorului."""
    # Obținem toate activitățile atribuite utilizatorului
    activities = Activity.objects.filter(
        assigned_to=request.user
    ).select_related('project', 'objective').order_by('due_date')
    
    # Aplicăm filtre
    status_filter = request.GET.get('status')
    if status_filter:
        activities = activities.filter(status=status_filter)
    
    project_filter = request.GET.get('project')
    if project_filter:
        activities = activities.filter(project_id=project_filter)
    
    search_query = request.GET.get('search')
    if search_query:
        activities = activities.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Separăm activitățile după status pentru afișare
    overdue_tasks = activities.filter(
        due_date__lt=timezone.now().date(),
        status__in=['not_started', 'in_progress']
    )
    today_tasks = activities.filter(
        due_date=timezone.now().date(),
        status__in=['not_started', 'in_progress']
    )
    upcoming_tasks = activities.filter(
        due_date__gt=timezone.now().date(),
        status__in=['not_started', 'in_progress']
    )
    completed_tasks = activities.filter(status='completed')
    
    # Obținem proiectele pentru filtru
    user_projects = Project.objects.filter(
        members__user=request.user
    ).distinct()
    
    context = {
        'overdue_tasks': overdue_tasks,
        'today_tasks': today_tasks,
        'upcoming_tasks': upcoming_tasks,
        'completed_tasks': completed_tasks,
        'all_activities': activities,
        'user_projects': user_projects,
        'status_filter': status_filter,
        'project_filter': project_filter,
        'search_query': search_query,
        'status_choices': Activity.STATUS_CHOICES,
    }
    
    return render(request, 'tasks/my_tasks.html', context)

@login_required
def all_tasks(request):
    """Afișează toate task-urile din proiectele în care utilizatorul este membru."""
    # Obținem toate activitățile din proiectele utilizatorului
    user_project_ids = ProjectMember.objects.filter(
        user=request.user
    ).values_list('project_id', flat=True)
    
    activities = Activity.objects.filter(
        project_id__in=user_project_ids
    ).select_related('project', 'assigned_to', 'objective').order_by('due_date')
    
    # Aplicăm filtre
    status_filter = request.GET.get('status')
    if status_filter:
        activities = activities.filter(status=status_filter)
    
    project_filter = request.GET.get('project')
    if project_filter:
        activities = activities.filter(project_id=project_filter)
    
    assigned_filter = request.GET.get('assigned')
    if assigned_filter:
        if assigned_filter == 'me':
            activities = activities.filter(assigned_to=request.user)
        elif assigned_filter == 'unassigned':
            activities = activities.filter(assigned_to__isnull=True)
        else:
            activities = activities.filter(assigned_to_id=assigned_filter)
    
    search_query = request.GET.get('search')
    if search_query:
        activities = activities.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Paginare
    paginator = Paginator(activities, 20)  # 20 task-uri per pagină
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Obținem datele pentru filtre
    user_projects = Project.objects.filter(
        members__user=request.user
    ).distinct()
    
    team_members = User.objects.filter(
        project_memberships__project_id__in=user_project_ids
    ).distinct()
    
    context = {
        'page_obj': page_obj,
        'user_projects': user_projects,
        'team_members': team_members,
        'status_filter': status_filter,
        'project_filter': project_filter,
        'assigned_filter': assigned_filter,
        'search_query': search_query,
        'status_choices': Activity.STATUS_CHOICES,
    }
    
    return render(request, 'tasks/all_tasks.html', context)

@login_required
def create_task(request):
    """Creează un task nou."""
    # Obținem proiectele în care utilizatorul poate crea task-uri
    user_projects = Project.objects.filter(
        members__user=request.user,
        members__role__in=['leader', 'admin', 'researcher']
    ).distinct()
    
    if not user_projects.exists():
        messages.error(request, "Nu aveți permisiunea de a crea task-uri în niciun proiect.")
        return redirect('my_tasks')
    
    if request.method == 'POST':
        project_id = request.POST.get('project')
        project = get_object_or_404(Project, id=project_id)
        
        # Verificăm permisiunea
        if not ProjectMember.objects.filter(
            project=project, 
            user=request.user, 
            role__in=['leader', 'admin', 'researcher']
        ).exists():
            messages.error(request, "Nu aveți permisiunea de a crea task-uri în acest proiect.")
            return redirect('my_tasks')
        
        form = ActivityForm(project, request.POST)
        if form.is_valid():
            activity = form.save(commit=False)
            activity.project = project
            activity.save()
            
            # Creăm notificare pentru utilizatorul asignat
            if activity.assigned_to and activity.assigned_to != request.user:
                Notification.objects.create(
                    user=activity.assigned_to,
                    title=f"Task nou: {activity.title}",
                    message=f"Ai fost asignat la un nou task în proiectul '{project.title}'.",
                    notification_type='activity',
                    related_project=project,
                    related_activity=activity
                )
            
            messages.success(request, f"Task-ul '{activity.title}' a fost creat cu succes.")
            return redirect('my_tasks')
    else:
        # Dacă avem un proiect specificat în URL
        project_id = request.GET.get('project')
        if project_id:
            try:
                project = Project.objects.get(id=project_id)
                form = ActivityForm(project)
            except Project.DoesNotExist:
                form = ActivityForm()
        else:
            form = ActivityForm()
    
    context = {
        'form': form,
        'user_projects': user_projects,
    }
    
    return render(request, 'tasks/create.html', context)

@login_required
def task_detail(request, task_id):
    """Afișează detaliile unui task."""
    activity = get_object_or_404(Activity, id=task_id)
    project = activity.project
    
    # Verificăm dacă utilizatorul are acces
    if not ProjectMember.objects.filter(project=project, user=request.user).exists():
        messages.error(request, "Nu aveți acces la acest task.")
        return redirect('my_tasks')
    
    # Verificăm dacă utilizatorul poate edita task-ul
    can_edit = (
        ProjectMember.objects.filter(
            project=project, 
            user=request.user, 
            role__in=['leader', 'admin', 'researcher']
        ).exists() or 
        activity.assigned_to == request.user
    )
    
    context = {
        'activity': activity,
        'project': project,
        'can_edit': can_edit,
    }
    
    return render(request, 'tasks/detail.html', context)
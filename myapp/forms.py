from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import (
    Project, ProjectMember, Objective, Activity, Profile
)

class CustomUserCreationForm(UserCreationForm):
    """Formular personalizat pentru înregistrarea utilizatorilor."""
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True, max_length=30)
    last_name = forms.CharField(required=True, max_length=30)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Adăugăm clase Bootstrap la câmpuri
        for field_name in self.fields:
            self.fields[field_name].widget.attrs['class'] = 'form-control'
            
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
            # Creăm și un profil pentru utilizator
            Profile.objects.create(user=user)
        return user


class CustomAuthenticationForm(AuthenticationForm):
    """Formular personalizat pentru autentificare."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Adăugăm clase Bootstrap la câmpuri
        for field_name in self.fields:
            self.fields[field_name].widget.attrs['class'] = 'form-control'


class ProfileForm(forms.ModelForm):
    """Formular pentru editarea profilului utilizatorului."""
    class Meta:
        model = Profile
        fields = ['picture', 'bio', 'institution', 'position', 'phone', 'role']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'institution': forms.TextInput(attrs={'class': 'form-control'}),
            'position': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
        }


class ProjectForm(forms.ModelForm):
    """Formular pentru crearea și editarea proiectelor."""
    class Meta:
        model = Project
        fields = ['title', 'description', 'start_date', 'end_date', 'status']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date and start_date > end_date:
            raise forms.ValidationError("Data de sfârșit trebuie să fie după data de început.")
        
        return cleaned_data


class ObjectiveForm(forms.ModelForm):
    """Formular pentru crearea și editarea obiectivelor."""
    class Meta:
        model = Objective
        fields = ['title', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }


class ActivityForm(forms.ModelForm):
    """Formular pentru crearea și editarea activităților."""
    class Meta:
        model = Activity
        fields = ['title', 'description', 'objective', 'start_date', 'due_date', 'assigned_to', 'status']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'objective': forms.Select(attrs={'class': 'form-select'}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'due_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def __init__(self, project=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if project:
            # Filtrăm obiectivele și utilizatorii în funcție de proiect
            self.fields['objective'].queryset = Objective.objects.filter(project=project)
            member_users = User.objects.filter(project_memberships__project=project)
            self.fields['assigned_to'].queryset = member_users
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        due_date = cleaned_data.get('due_date')
        
        if start_date and due_date and start_date > due_date:
            raise forms.ValidationError("Data de finalizare trebuie să fie după data de început.")
        
        return cleaned_data
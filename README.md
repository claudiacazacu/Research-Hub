# ResearchHub - Platformă de Gestiune a Proiectelor de Cercetare

Această platformă reprezintă o aplicație web complexă pentru gestionarea proiectelor de cercetare științifică, dezvoltată în Django în cadrul unui proiect academic. Aplicația facilitează colaborarea în echipă, monitorizarea progresului și organizarea activităților de cercetare.

## 📌 Descriere

ResearchHub este o platformă web destinată cercetătorilor, coordonatorilor de proiecte și echipelor de cercetare pentru a gestiona eficient proiectele științifice. Platforma oferă instrumente complete pentru planificarea, monitorizarea și finalizarea proiectelor de cercetare, cu accent pe colaborarea în echipă și transparența procesului.

Aplicația include funcționalități avansate pentru gestionarea membrilor echipei, atribuirea de task-uri, monitorizarea termenelor și comunicarea în timp real prin sistemul de notificări.

## 🛠️ Tehnologii folosite

- **Backend**: [Django 5.2.1](https://www.djangoproject.com/) - framework web Python
- **Frontend**: [Bootstrap 5.3.0](https://getbootstrap.com/) - framework CSS responsive
- **Baza de date**: SQLite (pentru dezvoltare)
- **Autentificare**: Django Authentication System
- **Iconuri**: [Font Awesome 6.4.0](https://fontawesome.com/)
- **Stilizare**: CSS custom + Bootstrap components

## 🧩 Funcționalități principale

### 👥 Gestionarea utilizatorilor
- **Înregistrare și autentificare** - sistem complet de conturi utilizator
- **Profile personalizate** - informații detaliate despre cercetători
- **Roluri diferențiate** - Administrator, Cercetător, Coordonator, Evaluator

### 📋 Managementul proiectelor
- **Creare proiecte** - definirea scopului, perioadei și echipei
- **Statusuri proiect** - Schiță, Planificare, În desfășurare, Suspendat, Finalizat
- **Monitorizare progres** - calculare automată progres pe baza task-urilor completate

### 👥 Gestionarea echipelor
- **Membri proiect** - adăugare/eliminare membri cu roluri specifice
- **Roluri în echipă** - Lider, Cercetător, Asistent, Consultant
- **Permisiuni granulare** - acces controlat pe baza rolurilor

### ✅ Managementul task-urilor
- **Creare activități** - definirea clară a sarcinilor și termenelor
- **Atribuire responsabili** - asignarea task-urilor membrilor echipei
- **Statusuri activități** - Neîncepută, În desfășurare, În revizuire, Finalizată
- **Monitorizare termene** - alertare pentru deadlines apropiate

### 🔔 Sistem de notificări
- **Notificări în timp real** - alertare pentru evenimente importante
- **Tipuri notificări** - Deadline apropiat, Activitate nouă, Modificări echipă
- **Istoric complet** - păstrarea tuturor notificărilor pentru referință

## 🗂️ Structura proiectului

```
researchhub/
├── myapp/                      # Aplicația principală
│   ├── models.py              # Modele de date (Project, Activity, etc.)
│   ├── views.py               # Logica aplicației
│   ├── forms.py               # Formulare Django
│   ├── urls.py                # Rutele aplicației
│   ├── admin.py               # Configurare admin Django
│   └── templates/             # Template-uri HTML
│       ├── base.html          # Template de bază
│       ├── home.html          # Pagina principală
│       ├── auth/              # Template-uri autentificare
│       ├── projects/          # Template-uri proiecte
│       ├── tasks/             # Template-uri task-uri
│       └── teams/             # Template-uri echipe
├── numeproiect/               # Configurare Django
│   ├── settings.py            # Setări aplicație
│   ├── urls.py                # URL-uri principale
│   └── wsgi.py                # Configurare WSGI
└── manage.py                  # Script management Django
```

## 🖼️ Fluxul aplicației

1. **Autentificare** - utilizatorii se înregistrează și se autentifică
2. **Creare proiecte** - definirea obiectivelor și echipei de lucru
3. **Planificare activități** - descompunerea proiectului în task-uri concrete
4. **Execuție** - membrii echipei lucrează la task-urile atribuite
5. **Monitorizare** - urmărirea progresului și respectarea termenelor
6. **Finalizare** - completarea proiectului și generarea rapoartelor

## 🚀 Instalare și configurare

```bash
# Clonare repository
git clone [repository-url]
cd researchhub

# Crearea mediului virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# sau
venv\Scripts\activate     # Windows

# Instalarea dependințelor
pip install django==5.2.1

# Migrarea bazei de date
python manage.py makemigrations
python manage.py migrate

# Crearea unui superuser
python manage.py createsuperuser

# Rularea serverului de dezvoltare
python manage.py runserver
```

## 👤 Utilizare

1. Accesați `http://localhost:8000` în browser
2. Înregistrați-vă un cont nou sau autentificați-vă
3. Creați primul proiect de cercetare
4. Adăugați membri în echipă și definiți rolurile
5. Planificați activitățile și atribuiți responsabilii
6. Monitorizați progresul prin dashboard-ul de administrare

## 🎯 Caracteristici tehnice

- **Arhitectură MVC** - separarea clară a logicii, datelor și prezentării
- **Responsive design** - interfață adaptabilă pentru desktop și mobile
- **Securitate** - protecție CSRF, validare input, autentificare robustă
- **Scalabilitate** - structură modulară pentru dezvoltare ulterioară
- **Internaționalização** - suport pentru limba română

## 📊 Modele de date

- **Project** - informații complete despre proiecte
- **ProjectMember** - relația între utilizatori și proiecte cu roluri
- **Activity** - task-uri individuale cu deadlines și responsabili
- **Objective** - obiective strategice ale proiectelor
- **Notification** - sistem de comunicare și alertare
- **Profile** - informații extinse despre utilizatori

## 🔧 Dezvoltare ulterioară

Platforma poate fi extinsă cu:
- Gestionarea documentelor și fișierelor
- Managementul bugetului și cheltuielilor
- Rapoarte avansate și dashboard-uri analitice
- Integrare cu servicii externe (calendare, email)
- API REST pentru aplicații mobile

## 🖋️ Autor

**Dezvoltat ca proiect academic**
- Platformă web pentru gestionarea proiectelor de cercetare
- Implementare completă în Django cu funcționalități avansate
- Focus pe colaborarea în echipă și eficiența proceselor

> 📦 Acest proiect demonstrează competențele în dezvoltarea aplicațiilor web complexe cu Django, cu accent pe design responsiv, securitate și experiența utilizatorului.

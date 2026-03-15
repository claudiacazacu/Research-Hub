# ResearchHub - Platformă de Gestiune a Proiectelor de Cercetare

Această platformă reprezintă o aplicație web complexă pentru gestionarea proiectelor de cercetare științifică, dezvoltată în Django în cadrul unui proiect academic. Aplicația facilitează colaborarea în echipă, monitorizarea progresului și organizarea activităților de cercetare.

##  Descriere

ResearchHub este o platformă web destinată cercetătorilor, coordonatorilor de proiecte și echipelor de cercetare pentru a gestiona eficient proiectele științifice. Platforma oferă instrumente complete pentru planificarea, monitorizarea și finalizarea proiectelor de cercetare, cu accent pe colaborarea în echipă și transparența procesului.

Aplicația include funcționalități avansate pentru gestionarea membrilor echipei, atribuirea de task-uri, monitorizarea termenelor și comunicarea în timp real prin sistemul de notificări.

##  Tehnologii folosite

- **Backend**: [Django 5.2.1](https://www.djangoproject.com/) 
- **Frontend**: [Bootstrap 5.3.0](https://getbootstrap.com/) 
- **Baza de date**: SQLite (pentru dezvoltare)
- **Autentificare**: Django Authentication System
- **Iconuri**: [Font Awesome 6.4.0](https://fontawesome.com/)
- **Stilizare**: CSS custom + Bootstrap components

##  Funcționalități principale

###  Gestionarea utilizatorilor
- **Înregistrare și autentificare** - sistem complet de conturi utilizator
- **Profile personalizate** - informații detaliate despre cercetători
- **Roluri diferențiate** - Administrator, Cercetător, Coordonator, Evaluator

###  Managementul proiectelor
- **Creare proiecte** - definirea scopului, perioadei și echipei
- **Statusuri proiect** - Schiță, Planificare, În desfășurare, Suspendat, Finalizat
- **Monitorizare progres** - calculare automată progres pe baza task-urilor completate

###  Gestionarea echipelor
- **Membri proiect** - adăugare/eliminare membri cu roluri specifice
- **Roluri în echipă** - Lider, Cercetător, Asistent, Consultant
- **Permisiuni granulare** - acces controlat pe baza rolurilor

###  Managementul task-urilor
- **Creare activități** - definirea clară a sarcinilor și termenelor
- **Atribuire responsabili** - asignarea task-urilor membrilor echipei
- **Statusuri activități** - Neîncepută, În desfășurare, În revizuire, Finalizată
- **Monitorizare termene** - alertare pentru deadlines apropiate

###  Sistem de notificări
- **Notificări în timp real** - alertare pentru evenimente importante
- **Tipuri notificări** - Deadline apropiat, Activitate nouă, Modificări echipă
- **Istoric complet** - păstrarea tuturor notificărilor pentru referință

##  Structura proiectului

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

##  Fluxul aplicației

1. **Autentificare** - utilizatorii se înregistrează și se autentifică
2. **Creare proiecte** - definirea obiectivelor și echipei de lucru
3. **Planificare activități** - descompunerea proiectului în task-uri concrete
4. **Execuție** - membrii echipei lucrează la task-urile atribuite
5. **Monitorizare** - urmărirea progresului și respectarea termenelor
6. **Finalizare** - completarea proiectului și generarea rapoartelor

##  Alte informații

**Dezvoltat ca proiect academic**
- Platformă web pentru gestionarea proiectelor de cercetare
- Implementare completă în Django cu funcționalități avansate
- Focus pe colaborarea în echipă și eficiența proceselor


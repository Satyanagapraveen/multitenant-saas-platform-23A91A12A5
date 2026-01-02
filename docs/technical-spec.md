# Technical Specification

## Project Structure

```
MultiTenant-SaaS/
├── docker-compose.yml          # Docker orchestration for all services
├── submission.json             # Test credentials for evaluation
├── README.md                   # Project documentation
│
├── core/                       # Django Backend
│   ├── Dockerfile              # Backend container configuration
│   ├── entrypoint.sh           # Auto-migration & seed data script
│   ├── requirements.txt        # Python dependencies
│   ├── manage.py               # Django CLI
│   │
│   ├── core/                   # Django project settings
│   │   ├── settings.py         # Configuration (env-based)
│   │   ├── urls.py             # Root URL routing
│   │   └── wsgi.py             # WSGI application
│   │
│   ├── accounts/               # User & Authentication module
│   │   ├── models.py           # Custom User model
│   │   ├── views.py            # Auth endpoints (login, register, etc.)
│   │   ├── serializers.py      # DRF serializers
│   │   ├── permissions.py      # RBAC permission classes
│   │   ├── urls.py             # Auth routes
│   │   └── management/
│   │       └── commands/
│   │           └── seed_data.py  # Database seeding command
│   │
│   ├── tenants/                # Tenant management module
│   │   ├── models.py           # Tenant model
│   │   ├── views.py            # Tenant CRUD
│   │   └── urls.py             # Tenant routes
│   │
│   ├── projects/               # Project management module
│   │   ├── models.py           # Project model (tenant-scoped)
│   │   ├── views.py            # Project CRUD
│   │   ├── serializers.py      # Project serializers
│   │   └── urls.py             # Project routes
│   │
│   ├── tasks/                  # Task management module
│   │   ├── models.py           # Task model (tenant-scoped)
│   │   ├── views.py            # Task CRUD + status updates
│   │   ├── serializers.py      # Task serializers
│   │   └── urls.py             # Task routes
│   │
│   └── audit_logs/             # Audit logging module
│       ├── models.py           # AuditLog model
│       ├── views.py            # Log retrieval endpoints
│       └── urls.py             # Audit routes
│
├── frontend/                   # React Frontend
│   ├── Dockerfile              # Frontend container (multi-stage build)
│   ├── package.json            # Node.js dependencies
│   ├── vite.config.js          # Vite configuration
│   ├── tailwind.config.js      # Tailwind CSS configuration
│   │
│   └── src/
│       ├── main.jsx            # Application entry point
│       ├── App.jsx             # Root component with routing
│       ├── index.css           # Global styles (Tailwind)
│       │
│       ├── api/
│       │   └── axios.js        # Configured Axios instance
│       │
│       ├── context/
│       │   └── AuthContext.jsx # Authentication state management
│       │
│       ├── components/
│       │   ├── Navbar.jsx      # Navigation component
│       │   └── ProtectedRoute.jsx  # Route guard
│       │
│       ├── layouts/
│       │   └── AppLayout.jsx   # Main application layout
│       │
│       ├── auth/
│       │   ├── Login.jsx       # Login page
│       │   └── Register.jsx    # Tenant registration page
│       │
│       └── pages/
│           ├── Dashboard.jsx   # Main dashboard
│           ├── Projects.jsx    # Project management
│           ├── Tasks.jsx       # Task kanban board
│           ├── Users.jsx       # User management
│           └── LandingPage.jsx # Public landing page
│
└── docs/                       # Documentation
    ├── API.md                  # API documentation
    ├── architecture.md         # System architecture
    ├── PRD.md                  # Product requirements
    ├── research.md             # Technology research
    ├── technical-spec.md       # This file
    └── images/                 # Architecture diagrams
```

---

## Development Setup Guide

### Prerequisites

| Tool           | Version | Purpose                       |
| -------------- | ------- | ----------------------------- |
| Python         | 3.11+   | Backend runtime               |
| Node.js        | 18+     | Frontend runtime              |
| Docker         | 20+     | Containerization              |
| Docker Compose | 2.0+    | Multi-container orchestration |
| Git            | 2.0+    | Version control               |

### Environment Variables

All environment variables are configured in `docker-compose.yml`:

```yaml
# Database Configuration
DB_HOST: database # PostgreSQL service name
DB_PORT: 5432 # Database port
DB_NAME: saas_db # Database name
DB_USER: postgres # Database user
DB_PASSWORD: postgres # Database password

# Django Configuration
SECRET_KEY: <secure-key> # Django secret key
DEBUG: "True" # Debug mode
ALLOWED_HOSTS: localhost,127.0.0.1,backend,0.0.0.0

# JWT Configuration
JWT_SECRET: <jwt-secret> # JWT signing key

# CORS Configuration
CORS_ALLOWED_ORIGINS: http://localhost:3000,http://frontend:3000
```

### Docker Setup (Recommended)

**Start all services:**

```bash
docker-compose up -d
```

**Check service status:**

```bash
docker-compose ps
```

**View logs:**

```bash
docker-compose logs -f backend
docker-compose logs -f frontend
```

**Stop all services:**

```bash
docker-compose down
```

**Reset database (fresh start):**

```bash
docker-compose down -v
docker-compose up -d
```

### Local Development Setup

**Backend:**

```bash
cd core
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_data
python manage.py runserver 5000
```

**Frontend:**

```bash
cd frontend
npm install
npm run dev
```

---

## Service Configuration

### Database Service (PostgreSQL)

| Property       | Value                            |
| -------------- | -------------------------------- |
| Image          | postgres:15                      |
| Container Name | database                         |
| External Port  | 5432                             |
| Internal Port  | 5432                             |
| Volume         | db_data:/var/lib/postgresql/data |

### Backend Service (Django)

| Property       | Value              |
| -------------- | ------------------ |
| Build Context  | ./core             |
| Container Name | backend            |
| External Port  | 5000               |
| Internal Port  | 5000               |
| Depends On     | database (healthy) |

**Startup Process:**

1. Wait for database connection
2. Run Django migrations
3. Load seed data
4. Verify seed data integrity
5. Start Django development server

### Frontend Service (React)

| Property       | Value             |
| -------------- | ----------------- |
| Build Context  | ./frontend        |
| Container Name | frontend          |
| External Port  | 3000              |
| Internal Port  | 3000              |
| Depends On     | backend (healthy) |

**Build Process:**

1. Install npm dependencies
2. Build production bundle with Vite
3. Serve static files with `serve`

---

## Database Schema

### Core Tables

**tenants**

- `id` (UUID, PK)
- `name` (VARCHAR)
- `subdomain` (VARCHAR, unique)
- `status` (ENUM: active, inactive, suspended)
- `subscription_plan` (ENUM: free, pro, enterprise)
- `max_users` (INT)
- `max_projects` (INT)
- `created_at` (TIMESTAMP)

**users**

- `id` (UUID, PK)
- `email` (VARCHAR, unique)
- `password` (VARCHAR, hashed)
- `full_name` (VARCHAR)
- `role` (ENUM: super_admin, tenant_admin, user)
- `tenant_id` (UUID, FK → tenants, nullable)
- `is_active` (BOOLEAN)
- `is_staff` (BOOLEAN)
- `is_superuser` (BOOLEAN)
- `created_at` (TIMESTAMP)

**projects**

- `id` (UUID, PK)
- `name` (VARCHAR)
- `description` (TEXT)
- `status` (ENUM: active, archived, completed)
- `tenant_id` (UUID, FK → tenants)
- `created_by_id` (UUID, FK → users)
- `created_at` (TIMESTAMP)
- `updated_at` (TIMESTAMP)

**tasks**

- `id` (UUID, PK)
- `title` (VARCHAR)
- `description` (TEXT)
- `status` (ENUM: todo, in_progress, completed)
- `priority` (ENUM: low, medium, high)
- `project_id` (UUID, FK → projects)
- `tenant_id` (UUID, FK → tenants)
- `assigned_to_id` (UUID, FK → users, nullable)
- `due_date` (DATE, nullable)
- `created_at` (TIMESTAMP)
- `updated_at` (TIMESTAMP)

**audit_logs**

- `id` (UUID, PK)
- `user_id` (UUID, FK → users)
- `tenant_id` (UUID, FK → tenants, nullable)
- `action` (VARCHAR)
- `resource_type` (VARCHAR)
- `resource_id` (UUID)
- `details` (JSON)
- `ip_address` (VARCHAR)
- `created_at` (TIMESTAMP)

---

## API Endpoints Summary

| #   | Method | Endpoint                    | Description         |
| --- | ------ | --------------------------- | ------------------- |
| 1   | POST   | /api/auth/register-tenant   | Register new tenant |
| 2   | POST   | /api/auth/login             | User login          |
| 3   | POST   | /api/auth/logout            | User logout         |
| 4   | GET    | /api/auth/me                | Get current user    |
| 5   | GET    | /api/tenants/               | List all tenants    |
| 6   | GET    | /api/tenants/:id            | Get tenant details  |
| 7   | PUT    | /api/tenants/:id            | Update tenant       |
| 8   | POST   | /api/tenants/:id/users      | Add user to tenant  |
| 9   | GET    | /api/tenants/:id/users/list | List tenant users   |
| 10  | PUT    | /api/users/:id              | Update user         |
| 11  | DELETE | /api/users/:id              | Delete user         |
| 12  | GET    | /api/projects               | List projects       |
| 13  | POST   | /api/projects               | Create project      |
| 14  | PUT    | /api/projects/:id           | Update project      |
| 15  | DELETE | /api/projects/:id           | Delete project      |
| 16  | GET    | /api/projects/:id/tasks     | List project tasks  |
| 17  | POST   | /api/projects/:id/tasks     | Create task         |
| 18  | PUT    | /api/tasks/:id              | Update task         |
| 19  | DELETE | /api/tasks/:id/delete       | Delete task         |
| 20  | PATCH  | /api/tasks/:id/status       | Update task status  |
| 21  | GET    | /api/tasks                  | List my tasks       |
| 22  | GET    | /api/audit-logs/            | List audit logs     |
| 23  | GET    | /api/health                 | Health check        |

---

## Security Implementation

### Authentication

- JWT-based authentication using SimpleJWT
- 24-hour token expiry
- Secure password hashing with Django's PBKDF2

### Authorization

- Role-based access control (RBAC)
- Three roles: super_admin, tenant_admin, user
- Custom permission classes for each role

### Data Isolation

- All tenant-scoped queries filter by tenant_id
- Foreign key constraints enforce referential integrity
- Super admin bypass for platform management

### Input Validation

- Django REST Framework serializers
- Email validation
- Password strength requirements

---

## Testing

**Run all tests:**

```bash
cd core
python manage.py test
```

**Test coverage:**

- User registration and authentication
- Project CRUD operations
- Task CRUD and status updates
- Tenant isolation verification
- Permission enforcement

---

## Troubleshooting

### Common Issues

**Port already in use:**

```bash
# Find process using port
netstat -ano | findstr :5000

# Kill process
taskkill /PID <pid> /F
```

**Database connection refused:**

```bash
# Check if database is running
docker-compose ps database

# Restart database
docker-compose restart database
```

**Frontend can't connect to backend:**

- Ensure backend is running on port 5000
- Check CORS settings in Django
- Verify VITE_API_URL environment variable

**Seed data not loading:**

```bash
# Run seed manually
docker-compose exec backend python manage.py seed_data
```

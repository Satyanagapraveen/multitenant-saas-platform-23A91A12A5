# System Architecture Document

## Multi-Tenant SaaS Platform - Project & Task Management System

---

## Table of Contents

1. [System Architecture Overview](#1-system-architecture-overview)
2. [Component Architecture](#2-component-architecture)
3. [Data Flow Diagrams](#3-data-flow-diagrams)
4. [API Architecture](#4-api-architecture)
5. [Database Schema](#5-database-schema)
6. [Development Setup Guide](#6-development-setup-guide)

---

## 1. System Architecture Overview

### High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              CLIENT LAYER                                    │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         Web Browser                                   │   │
│  │  ┌─────────────────────────────────────────────────────────────┐    │   │
│  │  │                    React SPA (Vite)                          │    │   │
│  │  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────────────┐   │    │   │
│  │  │  │  Auth   │ │Dashboard│ │Projects │ │     Tasks       │   │    │   │
│  │  │  │ Pages   │ │  Page   │ │  Pages  │ │ (List/Kanban)   │   │    │   │
│  │  │  └─────────┘ └─────────┘ └─────────┘ └─────────────────┘   │    │   │
│  │  │         │           │           │              │            │    │   │
│  │  │         └───────────┴───────────┴──────────────┘            │    │   │
│  │  │                          │                                   │    │   │
│  │  │                    Axios HTTP Client                         │    │   │
│  │  │                    (JWT in Headers)                          │    │   │
│  │  └─────────────────────────────────────────────────────────────┘    │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      │ HTTPS (Port 5173 dev / 443 prod)
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              API LAYER                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                  Django REST Framework API                           │   │
│  │                      (Port 8000)                                     │   │
│  │  ┌─────────────────────────────────────────────────────────────┐    │   │
│  │  │                    Middleware Stack                          │    │   │
│  │  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐   │    │   │
│  │  │  │   CORS   │ │   JWT    │ │  Tenant  │ │    Audit     │   │    │   │
│  │  │  │ Handler  │ │   Auth   │ │ Isolation│ │   Logging    │   │    │   │
│  │  │  └──────────┘ └──────────┘ └──────────┘ └──────────────┘   │    │   │
│  │  └─────────────────────────────────────────────────────────────┘    │   │
│  │  ┌─────────────────────────────────────────────────────────────┐    │   │
│  │  │                      API Endpoints                           │    │   │
│  │  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌───────┐ │    │   │
│  │  │  │  Auth   │ │ Tenants │ │  Users  │ │Projects │ │ Tasks │ │    │   │
│  │  │  │  /auth  │ │/tenants │ │ /users  │ │/projects│ │/tasks │ │    │   │
│  │  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └───────┘ │    │   │
│  │  └─────────────────────────────────────────────────────────────┘    │   │
│  │  ┌─────────────────────────────────────────────────────────────┐    │   │
│  │  │                    Django ORM Layer                          │    │   │
│  │  └─────────────────────────────────────────────────────────────┘    │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      │ SQL Queries
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              DATA LAYER                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │              SQLite (Dev) / PostgreSQL (Prod)                        │   │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌──────────────┐  │   │
│  │  │ tenants │ │  users  │ │projects │ │  tasks  │ │  audit_logs  │  │   │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └──────────────┘  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Architecture Principles

1. **Separation of Concerns**: Frontend and backend are completely separate applications
2. **Stateless API**: JWT-based authentication, no server-side sessions
3. **Tenant Isolation**: All queries filtered by tenant_id at the ORM level
4. **RESTful Design**: Standard HTTP methods and status codes

---

## 2. Component Architecture

### Frontend Architecture (React)

```
frontend/
├── public/                    # Static assets
├── src/
│   ├── api/
│   │   └── axios.js          # Axios instance with interceptors
│   ├── auth/
│   │   ├── Login.jsx         # Login page
│   │   └── Register.jsx      # Tenant registration page
│   ├── components/
│   │   ├── Navbar.jsx        # Navigation component
│   │   ├── ProtectedRoute.jsx # Route guard component
│   │   └── KanbanBoard.jsx   # Drag-and-drop kanban
│   ├── context/
│   │   └── AuthContext.jsx   # Authentication state management
│   ├── layouts/
│   │   └── AppLayout.jsx     # Main app layout with navbar
│   ├── pages/
│   │   ├── Dashboard.jsx     # Dashboard with stats
│   │   ├── projects/
│   │   │   ├── ProjectsList.jsx
│   │   │   ├── ProjectDetails.jsx
│   │   │   ├── CreateProjectModal.jsx
│   │   │   └── EditProjectModal.jsx
│   │   ├── tasks/
│   │   │   ├── MyTasks.jsx
│   │   │   ├── CreateTaskModal.jsx
│   │   │   └── EditTaskModal.jsx
│   │   └── users/
│   │       ├── UsersList.jsx
│   │       ├── CreateUserModal.jsx
│   │       └── EditUserModal.jsx
│   ├── App.jsx               # Route definitions
│   ├── main.jsx              # React entry point
│   └── index.css             # Tailwind CSS imports
├── index.html
├── package.json
├── vite.config.js
└── tailwind.config.js
```

### Backend Architecture (Django)

```
core/
├── core/                      # Django project settings
│   ├── settings.py           # Configuration
│   ├── urls.py               # Root URL routing
│   └── wsgi.py               # WSGI entry point
├── accounts/                  # User management app
│   ├── models.py             # User model
│   ├── views.py              # Auth & user views
│   ├── serializers.py        # DRF serializers
│   ├── urls.py               # Auth routes
│   ├── permissions.py        # Custom permissions
│   └── management/
│       └── commands/
│           └── seed_data.py  # Database seeding command
├── tenants/                   # Tenant management app
│   ├── models.py             # Tenant model
│   ├── views.py              # Tenant views
│   ├── serializers.py        # Tenant serializers
│   └── urls.py               # Tenant routes
├── projects/                  # Project management app
│   ├── models.py             # Project model
│   ├── views.py              # Project views
│   ├── serializers.py        # Project serializers
│   └── urls.py               # Project routes
├── tasks/                     # Task management app
│   ├── models.py             # Task model
│   ├── views.py              # Task views
│   ├── serializers.py        # Task serializers
│   └── urls.py               # Task routes
├── audit_logs/                # Audit logging app
│   ├── models.py             # AuditLog model
│   ├── views.py              # Audit log views
│   ├── serializers.py        # Audit serializers
│   ├── urls.py               # Audit routes
│   └── utils.py              # Logging utility functions
├── manage.py
└── db.sqlite3                # SQLite database (dev only)
```

---

## 3. Data Flow Diagrams

### Authentication Flow

```
┌──────────┐     ┌──────────────┐     ┌───────────┐     ┌──────────┐
│  Client  │────>│ POST /login  │────>│  Validate │────>│  Issue   │
│          │     │              │     │ Credentials│     │   JWT    │
└──────────┘     └──────────────┘     └───────────┘     └──────────┘
     │                                                        │
     │  ┌─────────────────────────────────────────────────────┘
     │  │
     ▼  ▼
┌──────────┐     ┌──────────────┐     ┌───────────┐     ┌──────────┐
│  Store   │────>│ API Request  │────>│  Validate │────>│  Return  │
│   JWT    │     │ + JWT Header │     │    JWT    │     │   Data   │
└──────────┘     └──────────────┘     └───────────┘     └──────────┘
```

### Multi-Tenant Data Access Flow

```
┌──────────────────────────────────────────────────────────────────────────┐
│                        API Request with JWT                               │
└──────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                     1. JWT Middleware                                     │
│                     - Validate token                                      │
│                     - Extract user_id, tenant_id, role                   │
└──────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                     2. Permission Check                                   │
│                     - Verify role allows action                          │
│                     - Check resource ownership                           │
└──────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                     3. Tenant Isolation                                   │
│                     - Filter query by tenant_id                          │
│                     - Ensure data belongs to user's tenant               │
└──────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                     4. Database Query                                     │
│                     - Execute with tenant_id filter                      │
│                     - Return only tenant's data                          │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## 4. API Architecture

### API Endpoint Summary

| Module       | Endpoint                      | Method | Auth | Description                    |
| ------------ | ----------------------------- | ------ | ---- | ------------------------------ |
| **Auth**     | `/api/auth/register-tenant`   | POST   | No   | Register new tenant            |
|              | `/api/auth/login`             | POST   | No   | User login                     |
|              | `/api/auth/logout`            | POST   | Yes  | User logout                    |
|              | `/api/auth/me`                | GET    | Yes  | Get current user               |
| **Tenants**  | `/api/tenants/`               | GET    | Yes  | List all tenants (super_admin) |
|              | `/api/tenants/:id`            | GET    | Yes  | Get tenant details             |
|              | `/api/tenants/:id`            | PUT    | Yes  | Update tenant                  |
| **Users**    | `/api/tenants/:id/users`      | POST   | Yes  | Create user                    |
|              | `/api/tenants/:id/users/list` | GET    | Yes  | List tenant users              |
|              | `/api/users/:id`              | PUT    | Yes  | Update user                    |
|              | `/api/users/:id`              | DELETE | Yes  | Delete user                    |
| **Projects** | `/api/projects`               | GET    | Yes  | List projects                  |
|              | `/api/projects`               | POST   | Yes  | Create project                 |
|              | `/api/projects/:id`           | GET    | Yes  | Get project                    |
|              | `/api/projects/:id`           | PUT    | Yes  | Update project                 |
|              | `/api/projects/:id`           | DELETE | Yes  | Delete project                 |
| **Tasks**    | `/api/projects/:id/tasks`     | GET    | Yes  | List project tasks             |
|              | `/api/projects/:id/tasks`     | POST   | Yes  | Create task                    |
|              | `/api/tasks/:id`              | PUT    | Yes  | Update task                    |
|              | `/api/tasks/:id/status`       | PATCH  | Yes  | Update task status             |
|              | `/api/tasks/:id/delete`       | DELETE | Yes  | Delete task                    |
|              | `/api/tasks`                  | GET    | Yes  | Get my tasks                   |
| **Audit**    | `/api/audit-logs/`            | GET    | Yes  | List audit logs                |

---

## 5. Database Schema

### Entity Relationship Diagram

```
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│     TENANTS     │       │      USERS      │       │    PROJECTS     │
├─────────────────┤       ├─────────────────┤       ├─────────────────┤
│ id (PK, UUID)   │───┐   │ id (PK, UUID)   │───┐   │ id (PK, UUID)   │
│ name            │   │   │ tenant_id (FK)  │◄──┤   │ tenant_id (FK)  │◄──┐
│ subdomain (UQ)  │   │   │ email           │   │   │ name            │   │
│ status          │   │   │ password_hash   │   │   │ description     │   │
│ subscription_plan│   │   │ full_name       │   │   │ status          │   │
│ max_users       │   └──►│ role            │   │   │ created_by (FK) │◄──┤
│ max_projects    │       │ is_active       │   │   │ created_at      │   │
│ created_at      │       │ created_at      │   │   │ updated_at      │   │
│ updated_at      │       │ updated_at      │   │   └─────────────────┘   │
└─────────────────┘       └─────────────────┘   │                         │
                                 │              │   ┌─────────────────┐   │
                                 │              │   │      TASKS      │   │
                                 │              │   ├─────────────────┤   │
                                 │              │   │ id (PK, UUID)   │   │
                                 │              └──►│ tenant_id (FK)  │◄──┘
                                 │                  │ project_id (FK) │◄────┐
                                 │                  │ title           │     │
                                 └─────────────────►│ assigned_to (FK)│     │
                                                    │ description     │     │
                                                    │ status          │     │
                                                    │ priority        │     │
                                                    │ due_date        │     │
                                                    │ created_at      │     │
                                                    │ updated_at      │     │
                                                    └─────────────────┘     │
                                                                            │
┌─────────────────┐                                                        │
│   AUDIT_LOGS    │                                                        │
├─────────────────┤                                                        │
│ id (PK, UUID)   │                                                        │
│ tenant_id (FK)  │◄───────────────────────────────────────────────────────┘
│ user_id (FK)    │
│ action          │
│ entity_type     │
│ entity_id       │
│ ip_address      │
│ created_at      │
└─────────────────┘
```

---

## 6. Development Setup Guide

### Prerequisites

| Software | Version | Purpose          |
| -------- | ------- | ---------------- |
| Python   | 3.10+   | Backend runtime  |
| Node.js  | 18+     | Frontend runtime |
| npm      | 9+      | Package manager  |
| Git      | Latest  | Version control  |

### Environment Variables

**Backend (.env in core/ directory):**

```bash
# Django
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (PostgreSQL for production)
DATABASE_URL=postgres://user:pass@localhost:5432/dbname

# JWT
JWT_SECRET_KEY=your-jwt-secret
JWT_EXPIRY_HOURS=24

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:5173
```

**Frontend (.env in frontend/ directory):**

```bash
VITE_API_URL=http://127.0.0.1:8000/api
```

### Installation Steps

#### 1. Clone Repository

```bash
git clone <repository-url>
cd MultiTenant-Saas
```

#### 2. Backend Setup

```bash
# Navigate to backend
cd core

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install django djangorestframework djangorestframework-simplejwt django-cors-headers

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Seed demo data
python manage.py seed_data

# Start development server
python manage.py runserver
```

#### 3. Frontend Setup

```bash
# Navigate to frontend (new terminal)
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### How to Run Locally

1. **Start Backend** (Terminal 1):

   ```bash
   cd core
   venv\Scripts\activate  # Windows
   python manage.py runserver
   ```

   Backend runs at: `http://127.0.0.1:8000`

2. **Start Frontend** (Terminal 2):

   ```bash
   cd frontend
   npm run dev
   ```

   Frontend runs at: `http://localhost:5173`

3. **Access Application**:
   - Open browser: `http://localhost:5173`
   - Login with demo credentials (see below)

### Demo Credentials

| Role         | Email                 | Password  | Subdomain |
| ------------ | --------------------- | --------- | --------- |
| Super Admin  | superadmin@system.com | Admin@123 | N/A       |
| Tenant Admin | admin@demo.com        | Demo@123  | demo      |
| User         | user1@demo.com        | User@123  | demo      |
| User         | user2@demo.com        | User@123  | demo      |

### How to Run Tests

```bash
# Backend tests
cd core
python manage.py test

# Frontend tests (if configured)
cd frontend
npm test
```

### API Documentation

With the backend running, you can access the browsable API at:

- `http://127.0.0.1:8000/api/`

---

## Appendix: Technology Stack Summary

| Layer              | Technology                    | Version |
| ------------------ | ----------------------------- | ------- |
| Frontend Framework | React                         | 19.x    |
| Build Tool         | Vite                          | 7.x     |
| Styling            | Tailwind CSS                  | 4.x     |
| HTTP Client        | Axios                         | 1.x     |
| Drag & Drop        | @hello-pangea/dnd             | 18.x    |
| Routing            | React Router                  | 7.x     |
| Backend Framework  | Django                        | 5.x     |
| API Framework      | Django REST Framework         | 3.x     |
| Authentication     | djangorestframework-simplejwt | 5.x     |
| Database (Dev)     | SQLite                        | 3.x     |
| Database (Prod)    | PostgreSQL                    | 15+     |

# Multi-Tenant SaaS Platform

A full-stack project and task management platform built for teams who need isolated workspaces. Each organization (tenant) gets their own space with separate users, projects, and tasks - all running on a single deployment.

Built this as a production-ready reference for anyone looking to implement multi-tenancy in their own apps. Works great for agencies managing multiple clients, companies with separate departments, or any scenario where you need data isolation between groups.

---

## Features

- **Multi-tenant Architecture** - Complete data isolation between organizations using a shared database approach
- **Role-based Access Control** - Three roles: Super Admin (platform-wide), Tenant Admin (organization-wide), Regular User
- **JWT Authentication** - Secure token-based auth with 24-hour expiry
- **Project Management** - Full CRUD for projects with tenant-scoped access
- **Task Management with Kanban** - Drag-and-drop kanban board, status updates, priority levels
- **User Management** - Tenant admins can invite and manage users within their organization
- **Subscription Limits** - Enforce max users and projects per tenant based on plan
- **Audit Logging** - Track all important actions (who did what, when)
- **Health Check Endpoint** - Docker-ready health checks for orchestration
- **Responsive UI** - Works on desktop and mobile

---

## Tech Stack

### Frontend

| Technology        | Version | Purpose                  |
| ----------------- | ------- | ------------------------ |
| React             | 19.x    | UI framework             |
| Vite              | 7.x     | Build tool & dev server  |
| Tailwind CSS      | 4.x     | Styling                  |
| React Router      | 7.x     | Client-side routing      |
| @hello-pangea/dnd | 18.x    | Drag-and-drop for Kanban |
| Axios             | 1.x     | HTTP client              |
| React Hook Form   | 7.x     | Form handling            |

### Backend

| Technology            | Version | Purpose             |
| --------------------- | ------- | ------------------- |
| Python                | 3.11    | Runtime             |
| Django                | 5.1     | Web framework       |
| Django REST Framework | 3.14    | API toolkit         |
| SimpleJWT             | 5.3     | JWT authentication  |
| PostgreSQL            | 15      | Production database |
| SQLite                | 3.x     | Local development   |

### DevOps

| Technology     | Purpose                       |
| -------------- | ----------------------------- |
| Docker         | Containerization              |
| Docker Compose | Multi-container orchestration |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND (React)                        │
│                     http://localhost:3000                       │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP/REST
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      BACKEND (Django + DRF)                     │
│                     http://localhost:5000                       │
│  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────┐   │
│  │   Auth    │  │  Tenants  │  │ Projects  │  │   Tasks   │   │
│  │   JWT     │  │  Scoping  │  │   CRUD    │  │  Kanban   │   │
│  └───────────┘  └───────────┘  └───────────┘  └───────────┘   │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PostgreSQL Database                          │
│                    (Shared, Tenant-Scoped)                      │
│  ┌─────────┐  ┌─────────┐  ┌──────────┐  ┌─────────┐          │
│  │ Tenants │  │  Users  │  │ Projects │  │  Tasks  │          │
│  └─────────┘  └─────────┘  └──────────┘  └─────────┘          │
└─────────────────────────────────────────────────────────────────┘
```

### Multi-tenancy Model

We use a **shared database with tenant_id column** approach:

- Every tenant-scoped table has a `tenant_id` foreign key
- Queries are automatically filtered by the authenticated user's tenant
- Super admins can access all tenants; regular users see only their own

---

## Getting Started

### Prerequisites

Make sure you have these installed:

- Python 3.11+
- Node.js 18+
- npm or yarn
- Docker & Docker Compose (for containerized setup)

### Local Development Setup

**1. Clone the repo**

```bash
git clone https://github.com/Satyanagapraveen/multitenant-saas-platform-23A91A12A5
cd MultiTenant-SaaS
```

**2. Backend Setup**

```bash
cd core

# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Seed the database with demo data
python manage.py seed_data

# Start the server
python manage.py runserver 5000
```

**3. Frontend Setup** (new terminal)

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

**4. Open in browser**

- Frontend: http://localhost:3000
- Backend API: http://localhost:5000
- Admin panel: http://localhost:5000/admin

### Docker Setup (Recommended for Production)

Just run:

```bash
docker-compose up -d
```

That's it. Docker will:

1. Start PostgreSQL database
2. Run migrations automatically
3. Seed demo data
4. Start backend on port 5000
5. Start frontend on port 3000

Check if everything is healthy:

```bash
curl http://localhost:5000/api/health
# Should return: {"status": "ok", "database": "connected"}
```

---

## Demo Credentials

After running `python manage.py seed_data` or `docker-compose up`, you can login with:

| Role         | Email                 | Password  | Subdomain     |
| ------------ | --------------------- | --------- | ------------- |
| Super Admin  | superadmin1@system.com | Admin@123 | (leave empty) |
| Tenant Admin | admin@demo.com        | Demo@123  | demo          |
| Regular User | user1@demo.com        | User@123  | demo          |
| Regular User | user2@demo.com        | User@123  | demo          |

---

## Environment Variables

### Backend (.env)

```bash
# Database (only needed for PostgreSQL, SQLite used by default locally)
DB_HOST=localhost
DB_PORT=5432
DB_NAME=saas_db
DB_USER=postgres
DB_PASSWORD=your_password

# Django
SECRET_KEY=your-secret-key-min-50-characters
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# JWT
JWT_SECRET=your-jwt-secret-min-32-chars

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000
```

### Frontend (.env)

```bash
VITE_API_URL=http://localhost:5000/api
```

| Variable               | Required | Description                                  |
| ---------------------- | -------- | -------------------------------------------- |
| `DB_HOST`              | No\*     | Database host. If not set, uses SQLite       |
| `DB_PORT`              | No       | Database port (default: 5432)                |
| `DB_NAME`              | No       | Database name                                |
| `DB_USER`              | No       | Database username                            |
| `DB_PASSWORD`          | No       | Database password                            |
| `SECRET_KEY`           | Yes      | Django secret key for security               |
| `DEBUG`                | No       | Enable debug mode (default: False)           |
| `ALLOWED_HOSTS`        | Yes      | Comma-separated allowed hosts                |
| `JWT_SECRET`           | No       | JWT signing key (uses SECRET_KEY if not set) |
| `CORS_ALLOWED_ORIGINS` | No       | Allowed CORS origins                         |
| `VITE_API_URL`         | Yes      | Backend API URL for frontend                 |

\*If `DB_HOST` is not set, the app uses SQLite for local development.

---

## API Documentation

Full API docs are available at [docs/API.md](docs/API.md).

### Quick Reference

| Endpoint                    | Method         | Description                |
| --------------------------- | -------------- | -------------------------- |
| `/api/health`               | GET            | Health check               |
| `/api/auth/register-tenant` | POST           | Register new tenant        |
| `/api/auth/login`           | POST           | Login                      |
| `/api/auth/logout`          | POST           | Logout                     |
| `/api/auth/me`              | GET            | Get current user           |
| `/api/tenants/`             | GET            | List tenants (super admin) |
| `/api/tenants/{id}/`        | GET/PUT/DELETE | Tenant details             |
| `/api/tenants/{id}/users`   | GET/POST       | Tenant users               |
| `/api/projects`             | GET/POST       | List/create projects       |
| `/api/projects/{id}`        | GET/PUT/DELETE | Project details            |
| `/api/tasks`                | GET/POST       | List/create tasks          |
| `/api/tasks/{id}`           | GET/PUT/DELETE | Task details               |
| `/api/tasks/{id}/status`    | PATCH          | Update task status         |
| `/api/audit-logs/`          | GET            | Audit logs                 |

---

## Project Structure

```
MultiTenant-SaaS/
├── core/                       # Django backend
│   ├── accounts/               # User auth & management
│   ├── tenants/                # Tenant management
│   ├── projects/               # Project CRUD
│   ├── tasks/                  # Task management
│   ├── audit_logs/             # Audit logging
│   ├── core/                   # Django settings
│   ├── manage.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── entrypoint.sh
├── frontend/                   # React frontend
│   ├── src/
│   │   ├── auth/               # Login, Register pages
│   │   ├── pages/              # Dashboard, Projects, Tasks
│   │   ├── components/         # Navbar, ProtectedRoute
│   │   ├── context/            # AuthContext
│   │   ├── api/                # Axios config
│   │   └── App.jsx
│   ├── package.json
│   └── Dockerfile
├── docs/                       # Documentation
│   ├── API.md
│   ├── PRD.md
│   └── architecture.md
├── docker-compose.yml
├── submission.json
└── README.md
```

---

## Troubleshooting

**Backend won't start?**

- Check if port 5000 is already in use
- Make sure you've run migrations: `python manage.py migrate`

**Frontend shows blank page?**

- Clear browser cache or use incognito
- Check browser console for errors
- Verify backend is running

**Docker issues?**

- Make sure Docker Desktop is running
- Try `docker-compose down -v` then `docker-compose up -d --build`

**Login not working?**

- Did you run `python manage.py seed_data`?
- Check that you're using the correct subdomain for tenant users

---

## Contributing

1. Fork it
2. Create your feature branch (`git checkout -b feature/cool-thing`)
3. Commit your changes (`git commit -m 'Add cool thing'`)
4. Push to the branch (`git push origin feature/cool-thing`)
5. Open a Pull Request

---



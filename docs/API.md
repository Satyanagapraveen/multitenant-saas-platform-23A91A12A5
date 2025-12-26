# API Documentation

Base URL: `http://localhost:5000/api`

All endpoints (except health, login, and register) require a valid JWT token in the Authorization header:

```
Authorization: Bearer <your_jwt_token>
```

---

## Table of Contents

1. [Health Check](#1-health-check)
2. [Authentication](#2-authentication)
   - [Register Tenant](#21-register-tenant)
   - [Login](#22-login)
   - [Logout](#23-logout)
   - [Get Current User](#24-get-current-user)
3. [Tenant Management](#3-tenant-management)
   - [List Tenants](#31-list-tenants)
   - [Get Tenant](#32-get-tenant)
   - [Update Tenant](#33-update-tenant)
   - [Delete Tenant](#34-delete-tenant)
4. [User Management](#4-user-management)
   - [List Tenant Users](#41-list-tenant-users)
   - [Create User](#42-create-user)
   - [Update User](#43-update-user)
   - [Delete User](#44-delete-user)
5. [Projects](#5-projects)
   - [List Projects](#51-list-projects)
   - [Create Project](#52-create-project)
   - [Get Project](#53-get-project)
   - [Update Project](#54-update-project)
   - [Delete Project](#55-delete-project)
6. [Tasks](#6-tasks)
   - [List Tasks](#61-list-tasks)
   - [Create Task](#62-create-task)
   - [Get Task](#63-get-task)
   - [Update Task](#64-update-task)
   - [Delete Task](#65-delete-task)
   - [Update Task Status](#66-update-task-status)
7. [Audit Logs](#7-audit-logs)

---

## 1. Health Check

Check if the API is running and database is connected.

**Endpoint:** `GET /api/health`

**Auth Required:** No

**Response:**

```json
{
  "status": "ok",
  "database": "connected"
}
```

**Error Response (503):**

```json
{
  "status": "error",
  "database": "disconnected"
}
```

---

## 2. Authentication

### 2.1 Register Tenant

Create a new tenant with an admin user. This is the entry point for new organizations.

**Endpoint:** `POST /api/auth/register-tenant`

**Auth Required:** No

**Request Body:**

```json
{
  "tenantName": "Acme Corp",
  "subdomain": "acme",
  "fullName": "John Admin",
  "email": "john@acme.com",
  "password": "SecurePass123"
}
```

| Field      | Type   | Required | Description                                  |
| ---------- | ------ | -------- | -------------------------------------------- |
| tenantName | string | Yes      | Organization name                            |
| subdomain  | string | Yes      | Unique subdomain (letters, numbers, hyphens) |
| fullName   | string | Yes      | Admin user's full name                       |
| email      | string | Yes      | Admin user's email                           |
| password   | string | Yes      | Min 8 characters                             |

**Success Response (201):**

```json
{
  "success": true,
  "message": "Tenant registered successfully",
  "data": {
    "tenant": {
      "id": "uuid",
      "name": "Acme Corp",
      "subdomain": "acme"
    },
    "user": {
      "id": "uuid",
      "email": "john@acme.com",
      "fullName": "John Admin",
      "role": "tenant_admin"
    }
  }
}
```

**Error Response (400):**

```json
{
  "success": false,
  "message": "Subdomain already taken"
}
```

---

### 2.2 Login

Authenticate a user and get JWT token.

**Endpoint:** `POST /api/auth/login`

**Auth Required:** No

**Request Body:**

```json
{
  "email": "admin@demo.com",
  "password": "Demo@123",
  "tenantSubdomain": "demo"
}
```

| Field           | Type   | Required | Description                                      |
| --------------- | ------ | -------- | ------------------------------------------------ |
| email           | string | Yes      | User's email                                     |
| password        | string | Yes      | User's password                                  |
| tenantSubdomain | string | No\*     | Required for tenant users, empty for super_admin |

\*Super admins don't need subdomain, tenant users must provide it.

**Success Response (200):**

```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "id": "uuid",
    "email": "admin@demo.com",
    "fullName": "Demo Admin",
    "role": "tenant_admin",
    "tenantId": "uuid"
  }
}
```

**Error Response (401):**

```json
{
  "success": false,
  "message": "Invalid credentials"
}
```

---

### 2.3 Logout

Invalidate the current token (client-side token removal).

**Endpoint:** `POST /api/auth/logout`

**Auth Required:** Yes

**Response (200):**

```json
{
  "success": true,
  "message": "Logged out successfully"
}
```

---

### 2.4 Get Current User

Get the authenticated user's profile.

**Endpoint:** `GET /api/auth/me`

**Auth Required:** Yes

**Response (200):**

```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "email": "admin@demo.com",
    "fullName": "Demo Admin",
    "role": "tenant_admin",
    "tenant": {
      "id": "uuid",
      "name": "Demo Company",
      "subdomain": "demo"
    }
  }
}
```

---

## 3. Tenant Management

### 3.1 List Tenants

Get all tenants. Only super_admin can access.

**Endpoint:** `GET /api/tenants/`

**Auth Required:** Yes (super_admin only)

**Query Parameters:**
| Param | Type | Description |
|-------|------|-------------|
| status | string | Filter by status (active, inactive, suspended) |

**Response (200):**

```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "name": "Demo Company",
      "subdomain": "demo",
      "status": "active",
      "subscriptionPlan": "pro",
      "maxUsers": 20,
      "maxProjects": 20,
      "createdAt": "2025-01-01T00:00:00Z"
    }
  ]
}
```

---

### 3.2 Get Tenant

Get a specific tenant's details.

**Endpoint:** `GET /api/tenants/{id}/`

**Auth Required:** Yes (super_admin or tenant_admin of that tenant)

**Response (200):**

```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "name": "Demo Company",
    "subdomain": "demo",
    "status": "active",
    "subscriptionPlan": "pro",
    "maxUsers": 20,
    "maxProjects": 20,
    "currentUsers": 3,
    "currentProjects": 2,
    "createdAt": "2025-01-01T00:00:00Z",
    "updatedAt": "2025-01-01T00:00:00Z"
  }
}
```

---

### 3.3 Update Tenant

Update tenant details.

**Endpoint:** `PUT /api/tenants/{id}/`

**Auth Required:** Yes (super_admin or tenant_admin)

**Request Body:**

```json
{
  "name": "Updated Company Name",
  "status": "active",
  "subscriptionPlan": "enterprise",
  "maxUsers": 50,
  "maxProjects": 100
}
```

**Response (200):**

```json
{
  "success": true,
  "message": "Tenant updated successfully",
  "data": {
    "id": "uuid",
    "name": "Updated Company Name",
    "status": "active"
  }
}
```

---

### 3.4 Delete Tenant

Delete a tenant and all associated data.

**Endpoint:** `DELETE /api/tenants/{id}/`

**Auth Required:** Yes (super_admin only)

**Response (200):**

```json
{
  "success": true,
  "message": "Tenant deleted successfully"
}
```

---

## 4. User Management

### 4.1 List Tenant Users

Get all users belonging to a tenant.

**Endpoint:** `GET /api/tenants/{tenant_id}/users`

**Auth Required:** Yes (super_admin or tenant_admin of that tenant)

**Response (200):**

```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "email": "user1@demo.com",
      "fullName": "John Doe",
      "role": "user",
      "isActive": true,
      "createdAt": "2025-01-01T00:00:00Z"
    }
  ]
}
```

---

### 4.2 Create User

Create a new user in a tenant.

**Endpoint:** `POST /api/tenants/{tenant_id}/users`

**Auth Required:** Yes (tenant_admin of that tenant)

**Request Body:**

```json
{
  "email": "newuser@demo.com",
  "fullName": "New User",
  "password": "Password123",
  "role": "user"
}
```

| Field    | Type   | Required | Description                                |
| -------- | ------ | -------- | ------------------------------------------ |
| email    | string | Yes      | User's email (unique within tenant)        |
| fullName | string | Yes      | User's full name                           |
| password | string | Yes      | Min 8 characters                           |
| role     | string | No       | "user" or "tenant_admin" (default: "user") |

**Response (201):**

```json
{
  "success": true,
  "message": "User created successfully",
  "data": {
    "id": "uuid",
    "email": "newuser@demo.com",
    "fullName": "New User",
    "role": "user"
  }
}
```

**Error Response (400):**

```json
{
  "success": false,
  "message": "User limit reached for this tenant"
}
```

---

### 4.3 Update User

Update a user's details.

**Endpoint:** `PUT /api/tenants/{tenant_id}/users/{user_id}`

**Auth Required:** Yes (tenant_admin)

**Request Body:**

```json
{
  "fullName": "Updated Name",
  "role": "tenant_admin",
  "isActive": true
}
```

**Response (200):**

```json
{
  "success": true,
  "message": "User updated successfully"
}
```

---

### 4.4 Delete User

Remove a user from the tenant.

**Endpoint:** `DELETE /api/tenants/{tenant_id}/users/{user_id}`

**Auth Required:** Yes (tenant_admin)

**Response (200):**

```json
{
  "success": true,
  "message": "User deleted successfully"
}
```

---

## 5. Projects

### 5.1 List Projects

Get all projects for the current user's tenant.

**Endpoint:** `GET /api/projects`

**Auth Required:** Yes

**Query Parameters:**
| Param | Type | Description |
|-------|------|-------------|
| status | string | Filter by status (active, completed, archived) |

**Response (200):**

```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "name": "Website Redesign",
      "description": "Complete redesign of company website",
      "status": "active",
      "createdBy": {
        "id": "uuid",
        "fullName": "Demo Admin"
      },
      "taskCount": 5,
      "createdAt": "2025-01-01T00:00:00Z",
      "updatedAt": "2025-01-01T00:00:00Z"
    }
  ]
}
```

---

### 5.2 Create Project

Create a new project.

**Endpoint:** `POST /api/projects`

**Auth Required:** Yes (tenant_admin or user)

**Request Body:**

```json
{
  "name": "New Project",
  "description": "Project description here"
}
```

| Field       | Type   | Required | Description         |
| ----------- | ------ | -------- | ------------------- |
| name        | string | Yes      | Project name        |
| description | string | No       | Project description |

**Response (201):**

```json
{
  "success": true,
  "message": "Project created successfully",
  "data": {
    "id": "uuid",
    "name": "New Project",
    "description": "Project description here",
    "status": "active"
  }
}
```

**Error Response (400):**

```json
{
  "success": false,
  "message": "Project limit reached for this tenant"
}
```

---

### 5.3 Get Project

Get project details with its tasks.

**Endpoint:** `GET /api/projects/{id}`

**Auth Required:** Yes

**Response (200):**

```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "name": "Website Redesign",
    "description": "Complete redesign",
    "status": "active",
    "createdBy": {
      "id": "uuid",
      "fullName": "Demo Admin"
    },
    "tasks": [
      {
        "id": "uuid",
        "title": "Design mockup",
        "status": "in_progress"
      }
    ],
    "createdAt": "2025-01-01T00:00:00Z"
  }
}
```

---

### 5.4 Update Project

Update project details.

**Endpoint:** `PUT /api/projects/{id}`

**Auth Required:** Yes (creator or tenant_admin)

**Request Body:**

```json
{
  "name": "Updated Project Name",
  "description": "Updated description",
  "status": "completed"
}
```

**Response (200):**

```json
{
  "success": true,
  "message": "Project updated successfully",
  "data": {
    "id": "uuid",
    "name": "Updated Project Name",
    "status": "completed"
  }
}
```

---

### 5.5 Delete Project

Delete a project and all its tasks.

**Endpoint:** `DELETE /api/projects/{id}`

**Auth Required:** Yes (creator or tenant_admin)

**Response (200):**

```json
{
  "success": true,
  "message": "Project deleted successfully"
}
```

---

## 6. Tasks

### 6.1 List Tasks

Get tasks. Can filter by project.

**Endpoint:** `GET /api/tasks`

**Auth Required:** Yes

**Query Parameters:**
| Param | Type | Description |
|-------|------|-------------|
| project | uuid | Filter by project ID |
| status | string | Filter by status (todo, in_progress, completed) |
| assignedTo | uuid | Filter by assigned user |

**Response (200):**

```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "title": "Design homepage mockup",
      "description": "Create high-fidelity mockup",
      "status": "in_progress",
      "priority": "high",
      "project": {
        "id": "uuid",
        "name": "Website Redesign"
      },
      "assignedTo": {
        "id": "uuid",
        "fullName": "John Doe"
      },
      "dueDate": "2025-01-15",
      "createdAt": "2025-01-01T00:00:00Z"
    }
  ]
}
```

---

### 6.2 Create Task

Create a new task in a project.

**Endpoint:** `POST /api/tasks`

**Auth Required:** Yes

**Request Body:**

```json
{
  "title": "New Task",
  "description": "Task description",
  "projectId": "uuid",
  "assignedTo": "uuid",
  "priority": "medium",
  "dueDate": "2025-01-20"
}
```

| Field       | Type   | Required | Description                         |
| ----------- | ------ | -------- | ----------------------------------- |
| title       | string | Yes      | Task title                          |
| description | string | No       | Task description                    |
| projectId   | uuid   | Yes      | Project this task belongs to        |
| assignedTo  | uuid   | No       | User to assign task to              |
| priority    | string | No       | low, medium, high (default: medium) |
| dueDate     | date   | No       | Due date (YYYY-MM-DD)               |

**Response (201):**

```json
{
  "success": true,
  "message": "Task created successfully",
  "data": {
    "id": "uuid",
    "title": "New Task",
    "status": "todo"
  }
}
```

---

### 6.3 Get Task

Get task details.

**Endpoint:** `GET /api/tasks/{id}`

**Auth Required:** Yes

**Response (200):**

```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "title": "Design homepage mockup",
    "description": "Create high-fidelity mockup for the new homepage",
    "status": "in_progress",
    "priority": "high",
    "project": {
      "id": "uuid",
      "name": "Website Redesign"
    },
    "assignedTo": {
      "id": "uuid",
      "fullName": "John Doe",
      "email": "john@demo.com"
    },
    "dueDate": "2025-01-15",
    "createdAt": "2025-01-01T00:00:00Z",
    "updatedAt": "2025-01-05T00:00:00Z"
  }
}
```

---

### 6.4 Update Task

Update task details.

**Endpoint:** `PUT /api/tasks/{id}`

**Auth Required:** Yes

**Request Body:**

```json
{
  "title": "Updated Task Title",
  "description": "Updated description",
  "assignedTo": "uuid",
  "priority": "high",
  "dueDate": "2025-01-25"
}
```

**Response (200):**

```json
{
  "success": true,
  "message": "Task updated successfully",
  "data": {
    "id": "uuid",
    "title": "Updated Task Title"
  }
}
```

---

### 6.5 Delete Task

Delete a task.

**Endpoint:** `DELETE /api/tasks/{id}`

**Auth Required:** Yes (creator, assignee, or tenant_admin)

**Response (200):**

```json
{
  "success": true,
  "message": "Task deleted successfully"
}
```

---

### 6.6 Update Task Status

Quick endpoint to update just the task status (for Kanban drag-drop).

**Endpoint:** `PATCH /api/tasks/{id}/status`

**Auth Required:** Yes

**Request Body:**

```json
{
  "status": "completed"
}
```

| Field  | Type   | Required | Description                     |
| ------ | ------ | -------- | ------------------------------- |
| status | string | Yes      | todo, in_progress, or completed |

**Response (200):**

```json
{
  "success": true,
  "message": "Status updated",
  "data": {
    "id": "uuid",
    "status": "completed"
  }
}
```

---

## 7. Audit Logs

Get audit logs for the tenant.

**Endpoint:** `GET /api/audit-logs/`

**Auth Required:** Yes (tenant_admin)

**Query Parameters:**
| Param | Type | Description |
|-------|------|-------------|
| action | string | Filter by action (CREATE, UPDATE, DELETE) |
| entityType | string | Filter by entity (User, Project, Task) |
| userId | uuid | Filter by user who performed action |

**Response (200):**

```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "action": "CREATE",
      "entityType": "Project",
      "entityId": "uuid",
      "description": "Created project 'Website Redesign'",
      "user": {
        "id": "uuid",
        "fullName": "Demo Admin"
      },
      "ipAddress": "192.168.1.1",
      "timestamp": "2025-01-01T10:30:00Z"
    }
  ]
}
```

---

## Error Responses

All endpoints return consistent error formats:

**400 Bad Request:**

```json
{
  "success": false,
  "message": "Validation error message",
  "errors": {
    "field_name": ["Error detail"]
  }
}
```

**401 Unauthorized:**

```json
{
  "success": false,
  "message": "Authentication required"
}
```

**403 Forbidden:**

```json
{
  "success": false,
  "message": "You don't have permission to perform this action"
}
```

**404 Not Found:**

```json
{
  "success": false,
  "message": "Resource not found"
}
```

**500 Internal Server Error:**

```json
{
  "success": false,
  "message": "An unexpected error occurred"
}
```

---

## Rate Limiting

Currently no rate limiting is implemented. For production, consider adding:

- 100 requests/minute for authenticated users
- 20 requests/minute for unauthenticated endpoints

---

## Testing with cURL

**Login:**

```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@demo.com","password":"Demo@123","tenantSubdomain":"demo"}'
```

**Get Projects (with token):**

```bash
curl http://localhost:5000/api/projects \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

**Create Task:**

```bash
curl -X POST http://localhost:5000/api/tasks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{"title":"New Task","projectId":"PROJECT_UUID","priority":"high"}'
```

# Database Entity Relationship Diagram (ERD)

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           MULTI-TENANT SAAS DATABASE                            │
│                              Entity Relationship Diagram                        │
└─────────────────────────────────────────────────────────────────────────────────┘

                                    ┌─────────────────────┐
                                    │      TENANTS        │
                                    ├─────────────────────┤
                                    │ PK  id (UUID)       │
                                    │     name            │
                                    │ UK  subdomain       │
                                    │     status          │
                                    │     subscription_   │
                                    │       plan          │
                                    │     max_users       │
                                    │     max_projects    │
                                    │     created_at      │
                                    │     updated_at      │
                                    └──────────┬──────────┘
                                               │
                                               │ 1
                                               │
               ┌───────────────────────────────┼───────────────────────────────┐
               │                               │                               │
               │ N                             │ N                             │ N
               ▼                               ▼                               ▼
┌──────────────────────────┐    ┌──────────────────────────┐    ┌──────────────────────────┐
│         USERS            │    │        PROJECTS          │    │       AUDIT_LOGS         │
├──────────────────────────┤    ├──────────────────────────┤    ├──────────────────────────┤
│ PK  id (UUID)            │    │ PK  id (UUID)            │    │ PK  id (UUID)            │
│ UK  email                │    │     name                 │    │ FK  user_id → USERS      │
│     password (hashed)    │    │     description          │    │ FK  tenant_id → TENANTS  │
│     full_name            │    │     status               │    │     action               │
│     role                 │    │ FK  tenant_id → TENANTS  │    │     resource_type        │
│ FK  tenant_id → TENANTS  │    │ FK  created_by → USERS   │    │     resource_id          │
│     is_active            │    │     created_at           │    │     details (JSON)       │
│     is_staff             │    │     updated_at           │    │     ip_address           │
│     is_superuser         │    └──────────────────────────┘    │     created_at           │
│     created_at           │                 │                  └──────────────────────────┘
│     updated_at           │                 │ 1
└──────────────────────────┘                 │
          │                                  │
          │                                  │
          │                    ┌─────────────┴─────────────┐
          │                    │                           │
          │ 1                  │ N                         │
          │                    ▼                           │
          │      ┌──────────────────────────┐              │
          │      │          TASKS           │              │
          │      ├──────────────────────────┤              │
          │      │ PK  id (UUID)            │              │
          │      │     title                │              │
          │      │     description          │              │
          │      │     status               │              │
          │      │     priority             │              │
          └──────│ FK  assigned_to → USERS  │              │
                 │ FK  project_id → PROJECTS│──────────────┘
                 │ FK  tenant_id → TENANTS  │
                 │     due_date             │
                 │     created_at           │
                 │     updated_at           │
                 └──────────────────────────┘


═══════════════════════════════════════════════════════════════════════════════════
                              RELATIONSHIP SUMMARY
═══════════════════════════════════════════════════════════════════════════════════

  TENANTS ─────┬───── 1:N ─────────────▶ USERS
               │
               ├───── 1:N ─────────────▶ PROJECTS
               │
               └───── 1:N ─────────────▶ AUDIT_LOGS

  USERS ───────┬───── 1:N ─────────────▶ PROJECTS (created_by)
               │
               ├───── 1:N ─────────────▶ TASKS (assigned_to)
               │
               └───── 1:N ─────────────▶ AUDIT_LOGS

  PROJECTS ────────── 1:N ─────────────▶ TASKS


═══════════════════════════════════════════════════════════════════════════════════
                              FIELD DEFINITIONS
═══════════════════════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────────────────────────┐
│                                  TENANTS                                        │
├────────────────────┬────────────────────┬───────────────────────────────────────┤
│ Field              │ Type               │ Description                           │
├────────────────────┼────────────────────┼───────────────────────────────────────┤
│ id                 │ UUID (PK)          │ Unique identifier                     │
│ name               │ VARCHAR(255)       │ Organization name                     │
│ subdomain          │ VARCHAR(100) UK    │ Unique subdomain identifier           │
│ status             │ ENUM               │ active, inactive, suspended           │
│ subscription_plan  │ ENUM               │ free, pro, enterprise                 │
│ max_users          │ INTEGER            │ Maximum allowed users                 │
│ max_projects       │ INTEGER            │ Maximum allowed projects              │
│ created_at         │ TIMESTAMP          │ Creation timestamp                    │
│ updated_at         │ TIMESTAMP          │ Last update timestamp                 │
└────────────────────┴────────────────────┴───────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────┐
│                                   USERS                                         │
├────────────────────┬────────────────────┬───────────────────────────────────────┤
│ Field              │ Type               │ Description                           │
├────────────────────┼────────────────────┼───────────────────────────────────────┤
│ id                 │ UUID (PK)          │ Unique identifier                     │
│ email              │ VARCHAR(255) UK    │ User email (login)                    │
│ password           │ VARCHAR(255)       │ Hashed password (PBKDF2)              │
│ full_name          │ VARCHAR(255)       │ User's full name                      │
│ role               │ ENUM               │ super_admin, tenant_admin, user       │
│ tenant_id          │ UUID (FK)          │ Associated tenant (null for super)    │
│ is_active          │ BOOLEAN            │ Account active status                 │
│ is_staff           │ BOOLEAN            │ Django admin access                   │
│ is_superuser       │ BOOLEAN            │ Django superuser flag                 │
│ created_at         │ TIMESTAMP          │ Creation timestamp                    │
│ updated_at         │ TIMESTAMP          │ Last update timestamp                 │
└────────────────────┴────────────────────┴───────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────┐
│                                  PROJECTS                                       │
├────────────────────┬────────────────────┬───────────────────────────────────────┤
│ Field              │ Type               │ Description                           │
├────────────────────┼────────────────────┼───────────────────────────────────────┤
│ id                 │ UUID (PK)          │ Unique identifier                     │
│ name               │ VARCHAR(255)       │ Project name                          │
│ description        │ TEXT               │ Project description                   │
│ status             │ ENUM               │ active, archived, completed           │
│ tenant_id          │ UUID (FK)          │ Owner tenant                          │
│ created_by_id      │ UUID (FK)          │ User who created the project          │
│ created_at         │ TIMESTAMP          │ Creation timestamp                    │
│ updated_at         │ TIMESTAMP          │ Last update timestamp                 │
└────────────────────┴────────────────────┴───────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────┐
│                                   TASKS                                         │
├────────────────────┬────────────────────┬───────────────────────────────────────┤
│ Field              │ Type               │ Description                           │
├────────────────────┼────────────────────┼───────────────────────────────────────┤
│ id                 │ UUID (PK)          │ Unique identifier                     │
│ title              │ VARCHAR(255)       │ Task title                            │
│ description        │ TEXT               │ Task description                      │
│ status             │ ENUM               │ todo, in_progress, completed          │
│ priority           │ ENUM               │ low, medium, high                     │
│ project_id         │ UUID (FK)          │ Parent project                        │
│ tenant_id          │ UUID (FK)          │ Owner tenant (denormalized)           │
│ assigned_to_id     │ UUID (FK)          │ Assigned user (nullable)              │
│ due_date           │ DATE               │ Task due date (nullable)              │
│ created_at         │ TIMESTAMP          │ Creation timestamp                    │
│ updated_at         │ TIMESTAMP          │ Last update timestamp                 │
└────────────────────┴────────────────────┴───────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────┐
│                                AUDIT_LOGS                                       │
├────────────────────┬────────────────────┬───────────────────────────────────────┤
│ Field              │ Type               │ Description                           │
├────────────────────┼────────────────────┼───────────────────────────────────────┤
│ id                 │ UUID (PK)          │ Unique identifier                     │
│ user_id            │ UUID (FK)          │ User who performed action             │
│ tenant_id          │ UUID (FK)          │ Tenant context (nullable)             │
│ action             │ VARCHAR(100)       │ Action type (CREATE, UPDATE, DELETE)  │
│ resource_type      │ VARCHAR(100)       │ Affected resource type                │
│ resource_id        │ UUID               │ Affected resource ID                  │
│ details            │ JSONB              │ Additional action details             │
│ ip_address         │ VARCHAR(45)        │ Client IP address                     │
│ created_at         │ TIMESTAMP          │ Action timestamp                      │
└────────────────────┴────────────────────┴───────────────────────────────────────┘


═══════════════════════════════════════════════════════════════════════════════════
                            MULTI-TENANCY MODEL
═══════════════════════════════════════════════════════════════════════════════════

  Data Isolation Strategy: SHARED DATABASE WITH TENANT_ID COLUMN

  ┌────────────────────────────────────────────────────────────────────────────┐
  │                                                                            │
  │   Every tenant-scoped query includes:                                      │
  │                                                                            │
  │   SELECT * FROM projects WHERE tenant_id = <user's tenant_id>              │
  │   SELECT * FROM tasks WHERE tenant_id = <user's tenant_id>                 │
  │   SELECT * FROM users WHERE tenant_id = <user's tenant_id>                 │
  │                                                                            │
  │   Super Admin Exception:                                                   │
  │   Super admins (tenant_id = NULL) can access ALL tenants' data             │
  │                                                                            │
  └────────────────────────────────────────────────────────────────────────────┘

═══════════════════════════════════════════════════════════════════════════════════
                                 INDEXES
═══════════════════════════════════════════════════════════════════════════════════

  • tenants.subdomain (UNIQUE)
  • users.email (UNIQUE)
  • users.tenant_id (INDEX)
  • projects.tenant_id (INDEX)
  • tasks.tenant_id (INDEX)
  • tasks.project_id (INDEX)
  • tasks.assigned_to_id (INDEX)
  • audit_logs.tenant_id (INDEX)
  • audit_logs.user_id (INDEX)
  • audit_logs.created_at (INDEX)
```

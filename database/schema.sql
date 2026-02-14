-- =====================================================
-- Multi-Tenant SaaS Platform - Database Schema
-- =====================================================
-- This file documents the database schema used by Django ORM.
-- Actual migrations are managed by Django in core/*/migrations/
-- =====================================================

-- =====================================================
-- Table: tenants
-- Purpose: Store organization/tenant information
-- =====================================================
CREATE TABLE tenants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    subdomain VARCHAR(100) UNIQUE NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'active',
        -- ENUM: 'active', 'suspended', 'trial'
    subscription_plan VARCHAR(20) NOT NULL DEFAULT 'free',
        -- ENUM: 'free', 'pro', 'enterprise'
    max_users INTEGER NOT NULL DEFAULT 5,
    max_projects INTEGER NOT NULL DEFAULT 3,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_tenants_subdomain ON tenants(subdomain);
CREATE INDEX idx_tenants_status ON tenants(status);

-- =====================================================
-- Table: users
-- Purpose: Store user accounts with tenant association
-- Note: Super admin users have tenant_id = NULL
-- =====================================================
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
        -- NULL for super_admin users
    email VARCHAR(254) NOT NULL,
    password VARCHAR(128) NOT NULL,  -- Hashed with bcrypt/argon2
    full_name VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL,
        -- ENUM: 'super_admin', 'tenant_admin', 'user'
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_staff BOOLEAN NOT NULL DEFAULT FALSE,
    is_superuser BOOLEAN NOT NULL DEFAULT FALSE,
    last_login TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Email unique per tenant (same email can exist in different tenants)
    CONSTRAINT unique_email_per_tenant UNIQUE (tenant_id, email)
);

-- Indexes
CREATE INDEX idx_users_tenant_id ON users(tenant_id);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);

-- =====================================================
-- Table: projects
-- Purpose: Store projects for each tenant
-- =====================================================
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(20) NOT NULL DEFAULT 'active',
        -- ENUM: 'active', 'archived', 'completed'
    created_by UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_projects_tenant_id ON projects(tenant_id);
CREATE INDEX idx_projects_status ON projects(status);
CREATE INDEX idx_projects_created_by ON projects(created_by);

-- =====================================================
-- Table: tasks
-- Purpose: Store tasks within projects
-- =====================================================
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(20) NOT NULL DEFAULT 'todo',
        -- ENUM: 'todo', 'in_progress', 'completed'
    priority VARCHAR(20) NOT NULL DEFAULT 'medium',
        -- ENUM: 'low', 'medium', 'high'
    assigned_to UUID REFERENCES users(id) ON DELETE SET NULL,
    due_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_tasks_project_id ON tasks(project_id);
CREATE INDEX idx_tasks_tenant_id ON tasks(tenant_id);
CREATE INDEX idx_tasks_assigned_to ON tasks(assigned_to);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_priority ON tasks(priority);
CREATE INDEX idx_tasks_tenant_project ON tasks(tenant_id, project_id);

-- =====================================================
-- Table: audit_logs
-- Purpose: Track all important actions for security audit
-- =====================================================
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(255) NOT NULL,
        -- Examples: 'CREATE_USER', 'DELETE_PROJECT', 'LOGIN', 'LOGOUT'
    entity_type VARCHAR(50),
        -- Examples: 'user', 'project', 'task', 'tenant'
    entity_id VARCHAR(255),
    ip_address INET,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_audit_logs_tenant_id ON audit_logs(tenant_id);
CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at);

-- =====================================================
-- Subscription Plan Limits Reference
-- =====================================================
-- Plan       | max_users | max_projects
-- -----------|-----------|-------------
-- free       | 5         | 3
-- pro        | 25        | 15
-- enterprise | 100       | 50
-- =====================================================

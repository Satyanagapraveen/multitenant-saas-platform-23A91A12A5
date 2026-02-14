-- =====================================================
-- Multi-Tenant SaaS Platform - Seed Data
-- =====================================================
-- This file documents the seed data structure.
-- Actual seeding is done via Django management command:
--   python manage.py seed_data
-- =====================================================

-- Note: Passwords are hashed using Django's password hashers (PBKDF2/bcrypt)
-- Plain text passwords shown here for documentation only

-- =====================================================
-- 1. Super Admin (No Tenant Association)
-- =====================================================
-- Email: superadmin@system.com
-- Password: Admin@123
-- Role: super_admin
-- tenant_id: NULL

-- =====================================================
-- 2. Demo Tenant
-- =====================================================
-- Name: Demo Company
-- Subdomain: demo
-- Status: active
-- Subscription Plan: pro
-- Max Users: 20
-- Max Projects: 20

-- =====================================================
-- 3. Tenant Admin for Demo Company
-- =====================================================
-- Email: admin@demo.com
-- Password: Demo@123
-- Role: tenant_admin
-- Tenant: Demo Company (subdomain: demo)

-- =====================================================
-- 4. Regular Users for Demo Company
-- =====================================================
-- User 1:
--   Email: user1@demo.com
--   Password: User@123
--   Full Name: John Doe
--   Role: user
--
-- User 2:
--   Email: user2@demo.com
--   Password: User@123
--   Full Name: Jane Smith
--   Role: user

-- =====================================================
-- 5. Sample Projects for Demo Company
-- =====================================================
-- Project 1:
--   Name: Website Redesign
--   Description: Complete redesign of the company website with modern UI/UX
--   Status: active
--   Created By: admin@demo.com
--
-- Project 2:
--   Name: Mobile App Development
--   Description: Build a cross-platform mobile app for customers
--   Status: active
--   Created By: admin@demo.com

-- =====================================================
-- 6. Sample Tasks
-- =====================================================
-- Tasks distributed across projects with various statuses and priorities
-- See core/accounts/management/commands/seed_data.py for full details

-- =====================================================
-- How to load seed data:
-- =====================================================
-- Automatic (Docker): Seed data loads automatically on container startup
-- Manual: python manage.py seed_data
-- Clear and re-seed: python manage.py seed_data --clear
-- =====================================================

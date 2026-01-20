-- 1. Permissions Table (System Static Registry)
CREATE TABLE permissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    slug TEXT UNIQUE NOT NULL, -- e.g., 'results:authorize'
    description TEXT,
    module_group TEXT NOT NULL -- 'lab', 'admin', 'billing'
);

-- 2. Roles Table (Dynamic Containers)
CREATE TABLE roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lab_id UUID REFERENCES labs(id) ON DELETE CASCADE, -- Nullable for System Defaults
    name TEXT NOT NULL,
    is_system_default BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Constraint: Role names should be unique per lab (or globally for defaults)
    CONSTRAINT unique_role_per_lab UNIQUE (lab_id, name)
);

-- 3. Role Permissions (Many-to-Many)
CREATE TABLE role_permissions (
    role_id UUID REFERENCES roles(id) ON DELETE CASCADE,
    permission_id UUID REFERENCES permissions(id) ON DELETE CASCADE,
    PRIMARY KEY (role_id, permission_id)
);

-- 4. User Table Updates (Linking to IAM)
-- Assuming 'users' table exists or creating a placeholder if this is a fresh start
-- Since 001 didn't create users (it focused on labs), we create 'users' now.
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT UNIQUE NOT NULL,
    hashed_password TEXT NOT NULL,
    full_name TEXT NOT NULL,
    lab_id UUID REFERENCES labs(id) ON DELETE CASCADE,
    role_id UUID REFERENCES roles(id) ON DELETE SET NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 5. Staff Invites (Secure Onboarding)
CREATE TABLE staff_invites (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lab_id UUID NOT NULL REFERENCES labs(id) ON DELETE CASCADE,
    email TEXT NOT NULL,
    role_id UUID NOT NULL REFERENCES roles(id),
    token_hash TEXT NOT NULL, -- Store hash, not raw token
    expires_at TIMESTAMPTZ NOT NULL,
    status TEXT DEFAULT 'pending', -- pending, accepted, expired
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ROW LEVEL SECURITY (RLS) POLICIES

ALTER TABLE roles ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE staff_invites ENABLE ROW LEVEL SECURITY;

-- Role Isolation: See roles for MY lab OR system defaults
CREATE POLICY role_isolation_policy ON roles
    USING (lab_id = current_setting('app.current_lab_id', true)::uuid OR is_system_default = TRUE);

-- User Isolation: See users in MY lab
CREATE POLICY user_isolation_policy ON users
    USING (lab_id = current_setting('app.current_lab_id', true)::uuid);

-- Invite Isolation: See invites for MY lab
CREATE POLICY invite_isolation_policy ON staff_invites
    USING (lab_id = current_setting('app.current_lab_id', true)::uuid)
    WITH CHECK (lab_id = current_setting('app.current_lab_id', true)::uuid);


-- SEEDING DEFAULT DATA

-- A. Permissions
INSERT INTO permissions (slug, description, module_group) VALUES
('onboarding:view', 'View onboarding status', 'admin'),
('lab:manage', 'Manage lab settings', 'admin'),
('staff:invite', 'Invite new staff', 'admin'),
('results:enter', 'Enter test results', 'lab'),
('results:authorize', 'Authorize final reports', 'lab'),
('reception:register', 'Register new patients', 'reception'),
('billing:view', 'View billing info', 'billing');

-- B. System Roles
-- We utilize a temporary function to grab IDs to handle the relations
DO $$
DECLARE
    admin_role_id UUID;
    tech_role_id UUID;
    recep_role_id UUID;
    p_rec RECORD;
BEGIN
    -- 1. Create System Roles
    INSERT INTO roles (name, is_system_default) VALUES ('Admin', TRUE) RETURNING id INTO admin_role_id;
    INSERT INTO roles (name, is_system_default) VALUES ('Technician', TRUE) RETURNING id INTO tech_role_id;
    INSERT INTO roles (name, is_system_default) VALUES ('Receptionist', TRUE) RETURNING id INTO recep_role_id;

    -- 2. Map Permissions
    -- Admin: ALL permissions
    FOR p_rec IN SELECT id FROM permissions LOOP
        INSERT INTO role_permissions (role_id, permission_id) VALUES (admin_role_id, p_rec.id);
    END LOOP;

    -- Technician: results:*
    FOR p_rec IN SELECT id FROM permissions WHERE slug LIKE 'results:%' LOOP
        INSERT INTO role_permissions (role_id, permission_id) VALUES (tech_role_id, p_rec.id);
    END LOOP;

    -- Receptionist: reception:*
    FOR p_rec IN SELECT id FROM permissions WHERE slug LIKE 'reception:%' LOOP
        INSERT INTO role_permissions (role_id, permission_id) VALUES (recep_role_id, p_rec.id);
    END LOOP;
END $$;

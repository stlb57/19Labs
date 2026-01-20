-- 1. Update Users Table (Security Fields)
-- Adding password_hash and uniqueness constraints
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS password_hash TEXT,
ADD COLUMN IF NOT EXISTS last_login_at TIMESTAMPTZ,
ADD CONSTRAINT users_email_unique UNIQUE (email);

-- 2. Refresh Tokens (Session Management)
CREATE TABLE refresh_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash TEXT NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    is_revoked BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Index for faster lookups during token rotation
    CONSTRAINT unique_active_token_hash UNIQUE (token_hash)
);

-- 3. Audit Logs (Security requirement)
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lab_id UUID REFERENCES labs(id) ON DELETE SET NULL,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    action TEXT NOT NULL, -- 'LOGIN_FAILED', 'Sign-up', etc.
    ip_address TEXT,
    details JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. RLS for New Tables
ALTER TABLE refresh_tokens ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;

-- Tokens: Only the user can see/rotate their own tokens
CREATE POLICY token_own_policy ON refresh_tokens
    USING (user_id = auth.uid()); -- In real implementation, this maps to the JWT sub

-- Audit: Admins see lab logs, Users see nothing (usually)
-- For now, allowing lab admins to see logs
CREATE POLICY audit_lab_policy ON audit_logs
    USING (lab_id = current_setting('app.current_lab_id', true)::uuid);

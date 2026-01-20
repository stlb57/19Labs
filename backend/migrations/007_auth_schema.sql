-- 1. Report Authorizations Table (The Lock & Seal)
CREATE TABLE report_authorizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lab_id UUID NOT NULL REFERENCES labs(id) ON DELETE CASCADE,
    booking_id UUID NOT NULL REFERENCES bookings(id) ON DELETE CASCADE,
    
    doctor_id UUID REFERENCES users(id), -- The Pathologist
    
    digital_signature_snapshot TEXT, -- Path to S3 image at time of signing
    ip_address TEXT, -- Audit compliance
    
    authorized_at TIMESTAMPTZ DEFAULT NOW(),
    
    CONSTRAINT unique_authorization_per_booking UNIQUE (booking_id)
);

-- 2. Result Amendments Table (Versioning)
-- Stores history of changes AFTER authorization
CREATE TABLE result_amendments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lab_id UUID NOT NULL REFERENCES labs(id) ON DELETE CASCADE,
    result_id UUID NOT NULL REFERENCES test_results(id) ON DELETE CASCADE,
    
    old_value TEXT,
    new_value TEXT,
    reason TEXT NOT NULL, -- Mandatory reason
    
    authorized_by UUID REFERENCES users(id),
    amended_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Update Bookings Table
ALTER TABLE bookings 
ADD COLUMN authorized_by UUID REFERENCES users(id),
ADD COLUMN authorized_at TIMESTAMPTZ;

-- RLS POLICIES
ALTER TABLE report_authorizations ENABLE ROW LEVEL SECURITY;
ALTER TABLE result_amendments ENABLE ROW LEVEL SECURITY;

-- Authorizations: See only my lab's
CREATE POLICY auth_isolation_policy ON report_authorizations
    USING (lab_id = current_setting('app.current_lab_id', true)::uuid);

-- Amendments: See only my lab's
CREATE POLICY amendment_isolation_policy ON result_amendments
    USING (lab_id = current_setting('app.current_lab_id', true)::uuid);

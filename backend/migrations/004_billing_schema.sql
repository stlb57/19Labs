-- Enable pg_trgm for fuzzy search if not already enabled
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- 1. Patients Table (Core Identity)
CREATE TABLE patients (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lab_id UUID NOT NULL REFERENCES labs(id) ON DELETE CASCADE,
    pid SERIAL, -- Lab-specific simple ID (e.g., 1001, 1002) - Note: Global serial, usually scoped via logic
    name TEXT NOT NULL,
    phone TEXT NOT NULL,
    email TEXT,
    age INTEGER,
    gender TEXT, -- 'M', 'F', 'O'
    address TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Constraint: Uniqueness per Lab? Or Global?
    -- Usually phone is unique per lab.
    CONSTRAINT unique_patient_phone_per_lab UNIQUE (lab_id, phone)
);

-- GIN Index for fast fuzzy search on Name and Phone
CREATE INDEX idx_patients_name_trgm ON patients USING gin (name gin_trgm_ops);
CREATE INDEX idx_patients_phone_trgm ON patients USING gin (phone gin_trgm_ops);


-- 2. Doctors Table (Referral Network)
CREATE TABLE doctors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lab_id UUID NOT NULL REFERENCES labs(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    specialization TEXT,
    contact TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Bookings Table (The "Order")
CREATE TABLE bookings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lab_id UUID NOT NULL REFERENCES labs(id) ON DELETE CASCADE,
    patient_id UUID NOT NULL REFERENCES patients(id),
    doctor_id UUID REFERENCES doctors(id), -- Nullable (Self-referral)
    
    booking_readable_id TEXT, -- e.g., 'LAB-2024-0001'
    
    total_amount NUMERIC(10, 2) NOT NULL DEFAULT 0,
    discount_amount NUMERIC(10, 2) DEFAULT 0,
    tax_amount NUMERIC(10, 2) DEFAULT 0,
    net_total NUMERIC(10, 2) NOT NULL DEFAULT 0,
    
    payment_method TEXT DEFAULT 'cash', -- 'cash', 'upi', 'card', 'due'
    payment_status TEXT DEFAULT 'pending', -- 'pending', 'partial', 'paid'
    workflow_status TEXT DEFAULT 'registered', -- 'registered', 'sample_collected', 'processing', 'authorized', 'completed'
    
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. Booking Items (Tests in the Cart)
CREATE TABLE booking_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    booking_id UUID NOT NULL REFERENCES bookings(id) ON DELETE CASCADE,
    test_id UUID REFERENCES master_clinical_tests(id), -- Link to master or lab_catalog? Ideally lab_catalog to lock price at time of booking
    -- Ideally we link to lab_catalog entry, but for simplicity we store metadata snapshot
    catalog_item_id UUID REFERENCES lab_catalog(id),
    
    test_name_snapshot TEXT NOT NULL, -- Snapshot name in case catalog changes
    price_snapshot NUMERIC(10, 2) NOT NULL, -- Snapshot price
    
    status TEXT DEFAULT 'pending' -- 'pending', 'result_entered', 'verified'
);

-- RLS POLICIES

ALTER TABLE patients ENABLE ROW LEVEL SECURITY;
ALTER TABLE doctors ENABLE ROW LEVEL SECURITY;
ALTER TABLE bookings ENABLE ROW LEVEL SECURITY;
ALTER TABLE booking_items ENABLE ROW LEVEL SECURITY;

-- Patients: See only my lab's
CREATE POLICY patient_isolation_policy ON patients
    USING (lab_id = current_setting('app.current_lab_id', true)::uuid);

-- Doctors: See only my lab's
CREATE POLICY doctor_isolation_policy ON doctors
    USING (lab_id = current_setting('app.current_lab_id', true)::uuid);

-- Bookings: See only my lab's
CREATE POLICY booking_isolation_policy ON bookings
    USING (lab_id = current_setting('app.current_lab_id', true)::uuid);

-- Items: Join bookings to check lab_id
CREATE POLICY booking_item_isolation_policy ON booking_items
    USING (
        booking_id IN (
            SELECT id FROM bookings 
            WHERE lab_id = current_setting('app.current_lab_id', true)::uuid
        )
    );

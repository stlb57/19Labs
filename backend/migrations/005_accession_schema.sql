-- 1. Accessions Table (The Physical Sample)
CREATE TABLE accessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lab_id UUID NOT NULL REFERENCES labs(id) ON DELETE CASCADE,
    booking_id UUID NOT NULL REFERENCES bookings(id) ON DELETE CASCADE,
    
    accession_number TEXT NOT NULL, -- Human Readable: 'LAB-2024-001-A'
    container_type TEXT NOT NULL, -- 'EDTA', 'Serum Separator', 'Urine Cup'
    volume_required_ml NUMERIC(4, 1), -- e.g. 2.5
    
    status TEXT DEFAULT 'pending', -- 'pending', 'collected', 'received', 'rejected', 'processed'
    
    collected_by UUID REFERENCES users(id),
    collected_at TIMESTAMPTZ,
    
    received_by UUID REFERENCES users(id),
    received_at TIMESTAMPTZ,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    CONSTRAINT unique_accession_number_per_lab UNIQUE (lab_id, accession_number)
);

-- 2. Accession Items (Linking Tests to Tubes)
-- Which items from the booking go into this tube?
CREATE TABLE accession_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    accession_id UUID NOT NULL REFERENCES accessions(id) ON DELETE CASCADE,
    booking_item_id UUID NOT NULL REFERENCES booking_items(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Rejection Logs (Audit Trail)
CREATE TABLE sample_rejection_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lab_id UUID NOT NULL REFERENCES labs(id) ON DELETE CASCADE,
    accession_id UUID NOT NULL REFERENCES accessions(id) ON DELETE CASCADE,
    
    reason TEXT NOT NULL, -- 'Hemolyzed', 'Clotted', 'Insufficient Volume'
    rejected_by UUID REFERENCES users(id),
    rejected_at TIMESTAMPTZ DEFAULT NOW(),
    
    notes TEXT
);

-- RLS POLICIES
ALTER TABLE accessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE accession_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE sample_rejection_logs ENABLE ROW LEVEL SECURITY;

-- Accessions: See only my lab's
CREATE POLICY accession_isolation_policy ON accessions
    USING (lab_id = current_setting('app.current_lab_id', true)::uuid);

-- Rejection Logs: See only my lab's
CREATE POLICY rejection_log_isolation_policy ON sample_rejection_logs
    USING (lab_id = current_setting('app.current_lab_id', true)::uuid);

-- Accession Items: Join accessions to check lab_id
CREATE POLICY accession_item_isolation_policy ON accession_items
    USING (
        accession_id IN (
            SELECT id FROM accessions 
            WHERE lab_id = current_setting('app.current_lab_id', true)::uuid
        )
    );

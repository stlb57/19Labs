-- Enable PostGIS for location-based queries
CREATE EXTENSION IF NOT EXISTS postgis;

-- 1. Labs Table (The Tenant)
CREATE TABLE labs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lab_name TEXT NOT NULL,
    owner_name TEXT NOT NULL,
    phone TEXT NOT NULL,
    whatsapp_phone TEXT,
    address TEXT NOT NULL,
    location GEOGRAPHY(POINT, 4326), -- PostGIS Point for 5km/10km radius logic
    google_place_id TEXT,
    license_no TEXT,
    logo_key TEXT,
    staff_limit INT DEFAULT 5,
    description TEXT,
    is_nabl_accredited BOOLEAN DEFAULT FALSE,
    profile_completion_score INT DEFAULT 0,
    is_setup_complete BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Master Clinical Tests (The Seed Library)
CREATE TABLE master_clinical_tests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    loinc_code TEXT UNIQUE,
    test_name TEXT NOT NULL,
    department TEXT NOT NULL, -- Hematology, Biochemistry, etc.
    analyte TEXT, -- e.g., "Glucose"
    sample_type TEXT, -- e.g., "Serum", "Whole Blood"
    description_template TEXT, -- Template: "{{test_name}} is a {{department}} test..."
    base_price_benchmark NUMERIC(10, 2), -- Global base price for reference
    default_ranges JSONB, -- { "male": { "min": 0, "max": 10 }, ... }
    icon_slug TEXT -- Mapped to local Lucide icon set
);

-- 3. Lab Catalog (Tenant-Specific Menu)
CREATE TABLE lab_catalog (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lab_id UUID NOT NULL REFERENCES labs(id) ON DELETE CASCADE,
    test_id UUID NOT NULL REFERENCES master_clinical_tests(id),
    price NUMERIC(10, 2) NOT NULL,
    tat_mins INT NOT NULL, -- Turnaround time
    instructions TEXT, -- "Fasting required"
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    CONSTRAINT unique_lab_test UNIQUE (lab_id, test_id)
);

-- Index for regional price aggregation (checking other labs' prices)
CREATE INDEX idx_lab_catalog_price ON lab_catalog (price);
CREATE INDEX idx_lab_catalog_test_id ON lab_catalog (test_id);

-- 4. Lab Documents (Secure Storage)
CREATE TABLE lab_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lab_id UUID NOT NULL REFERENCES labs(id) ON DELETE CASCADE,
    doc_type TEXT NOT NULL, -- 'NABL', 'LICENSE', 'LOGO'
    s3_key TEXT NOT NULL,
    mime_type TEXT,
    is_verified BOOLEAN DEFAULT FALSE,
    uploaded_at TIMESTAMPTZ DEFAULT NOW()
);

-- ROW LEVEL SECURITY (RLS) SETUP
ALTER TABLE labs ENABLE ROW LEVEL SECURITY;
ALTER TABLE lab_catalog ENABLE ROW LEVEL SECURITY;
ALTER TABLE lab_documents ENABLE ROW LEVEL SECURITY;

-- Policy: Lab can only see/edit their own data
-- Assuming auth.uid() returns the current user's ID which matches a lab owner or link
-- For simplicity in this SQL, we reference a hypothetic auth function or session variable.
-- In production, this binds to the JWT claims.

CREATE POLICY lab_isolation_policy ON labs
    USING (id = current_setting('app.current_lab_id', true)::uuid);

CREATE POLICY catalog_isolation_policy ON lab_catalog
    USING (lab_id = current_setting('app.current_lab_id', true)::uuid)
    WITH CHECK (lab_id = current_setting('app.current_lab_id', true)::uuid);

CREATE POLICY document_isolation_policy ON lab_documents
    USING (lab_id = current_setting('app.current_lab_id', true)::uuid)
    WITH CHECK (lab_id = current_setting('app.current_lab_id', true)::uuid);

-- Public/Regional Access Policies (Strictly Controlled)
-- Allow "Regional Intelligence" queries to read aggregate data but NOT specific lab info
-- This is usually handled via SECURITY DEFINER functions, but for catalog:
-- Labs need to be able to READ master_clinical_tests (Public)
ALTER TABLE master_clinical_tests ENABLE ROW LEVEL SECURITY;
CREATE POLICY master_tests_read_all ON master_clinical_tests
    FOR SELECT USING (true);


-- 5. Helper Functions for "No AI" Logic

-- Pricing Aggregator Algorithm: Average price for a test in 5km radius
CREATE OR REPLACE FUNCTION get_regional_avg_price(target_test_id UUID, ref_lat FLOAT, ref_long FLOAT, radius_meters FLOAT)
RETURNS NUMERIC AS $$
DECLARE
    avg_price NUMERIC;
BEGIN
    SELECT AVG(lc.price)
    INTO avg_price
    FROM lab_catalog lc
    JOIN labs l ON lc.lab_id = l.id
    WHERE lc.test_id = target_test_id
    AND ST_DWithin(
        l.location,
        ST_SetSRID(ST_MakePoint(ref_long, ref_lat), 4326),
        radius_meters
    );
    
    RETURN COALESCE(avg_price, 0);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

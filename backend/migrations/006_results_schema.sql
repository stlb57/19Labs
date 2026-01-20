-- 1. Test Results Table (The Core Data)
CREATE TABLE test_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lab_id UUID NOT NULL REFERENCES labs(id) ON DELETE CASCADE,
    accession_id UUID NOT NULL REFERENCES accessions(id) ON DELETE CASCADE,
    
    test_id UUID REFERENCES master_clinical_tests(id), -- Link to master definition
    parameter_slug TEXT NOT NULL, -- e.g. 'hemoglobin', 'total_cholesterol'
    
    raw_value TEXT, -- Stored as string to handle '< 0.5', 'Positive' etc.
    unit TEXT,
    
    flag TEXT DEFAULT 'normal', -- 'normal', 'high', 'low', 'panic', 'delta'
    is_draft BOOLEAN DEFAULT TRUE, -- TRUE = Technician Entry, FALSE = Committed for Review
    
    entered_by UUID REFERENCES users(id),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Constraint: One result per parameter per accession
    CONSTRAINT unique_result_per_accession UNIQUE (accession_id, parameter_slug)
);

-- 2. Result Audit Logs (Compliance Requirement)
-- Must track Old Value vs New Value for every update
CREATE TABLE result_audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lab_id UUID NOT NULL, -- Denormalized for RLS efficiency
    result_id UUID NOT NULL REFERENCES test_results(id) ON DELETE CASCADE,
    
    old_value TEXT,
    new_value TEXT,
    
    changed_by UUID, -- Captured from context or trigger if possible (hard in pure SQL trigger without session vars)
                     -- We will write to this table via App Logic for 'changed_by' accuracy, 
                     -- OR use a Trigger that reads current_setting('app.current_user_id')
    
    changed_at TIMESTAMPTZ DEFAULT NOW(),
    reason TEXT -- 'Typo Correction', 'Re-run'
);

-- 3. Audit Trigger Function
CREATE OR REPLACE FUNCTION log_result_changes()
RETURNS TRIGGER AS $$
BEGIN
    -- Only log if value actually changed and it was NOT a draft-to-draft minor edit? 
    -- Actually, NABL requires ALL edits to be logged once significant. 
    -- For now, we log everything if old_value IS DISTINCT FROM new_value
    IF (OLD.raw_value IS DISTINCT FROM NEW.raw_value) THEN
        INSERT INTO result_audit_logs (lab_id, result_id, old_value, new_value, changed_at)
        VALUES (OLD.lab_id, OLD.id, OLD.raw_value, NEW.raw_value, NOW());
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 4. Apply Trigger
CREATE TRIGGER trigger_log_result_update
AFTER UPDATE ON test_results
FOR EACH ROW
EXECUTE FUNCTION log_result_changes();


-- RLS POLICIES
ALTER TABLE test_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE result_audit_logs ENABLE ROW LEVEL SECURITY;

-- Results: See only my lab's
CREATE POLICY result_isolation_policy ON test_results
    USING (lab_id = current_setting('app.current_lab_id', true)::uuid);

-- Audit Logs: See only my lab's
CREATE POLICY audit_log_isolation_policy ON result_audit_logs
    USING (lab_id = current_setting('app.current_lab_id', true)::uuid);

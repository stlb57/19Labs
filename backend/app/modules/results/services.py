from uuid import UUID, uuid4
from typing import List, Dict
from datetime import datetime
from .schemas import ResultBatchUpdate, ResultRead, ResultEntry

# Mock Stores
MOCK_RESULTS = []

class FormulaEngine:
    """
    Deterministic Intelligence: Hardcoded Formulas.
    """
    def apply_formulas(self, current_results: List[ResultEntry]) -> List[ResultEntry]:
        # Convert to Dictionary for easier lookup
        data = {r.parameter_slug: r.raw_value for r in current_results}
        
        # 1. Globulin = Total Protein - Albumin
        if 'total_protein' in data and 'albumin' in data:
            try:
                tp = float(data['total_protein'])
                alb = float(data['albumin'])
                glob = round(tp - alb, 2)
                
                # Upsert Globulin
                self._upsert_result(current_results, 'globulin', str(glob))
            except ValueError:
                pass # Skip if non-numeric
                
        # 2. A/G Ratio
        if 'albumin' in data and 'globulin' in data: # Note: Globulin might have just been calculated
             try:
                alb = float(data['albumin'])
                glob = float(self._get_val(current_results, 'globulin'))
                if glob > 0:
                    ratio = round(alb / glob, 2)
                    self._upsert_result(current_results, 'ag_ratio', str(ratio))
             except:
                pass

        return current_results

    def _get_val(self, results, slug):
        r = next((x for x in results if x.parameter_slug == slug), None)
        return r.raw_value if r else None

    def _upsert_result(self, results, slug, value):
        existing = next((x for x in results if x.parameter_slug == slug), None)
        if existing:
            existing.raw_value = value
        else:
            results.append(ResultEntry(parameter_slug=slug, raw_value=value, flag="normal"))

class DeltaCheckService:
    async def flag_deltas(self, patient_id: UUID, current_results: List[ResultRead]):
        """
        Mock Logic: Check against 'Previous History'
        """
        # In real DB, we would query: SELECT * FROM results WHERE patient_id = :pid ORDER BY date DESC LIMIT 1
        # Here we simulate a previous Hemoglobin of 14.0
        mock_history = {'hemoglobin': '14.0', 'platelets': '250000'}
        
        for res in current_results:
            if res.parameter_slug in mock_history:
                prev = mock_history[res.parameter_slug]
                res.prev_value = prev
                
                # Check 30% Variance
                try:
                    curr_float = float(res.raw_value)
                    prev_float = float(prev)
                    diff = abs(curr_float - prev_float)
                    percentage = (diff / prev_float) * 100
                    
                    if percentage > 30:
                        res.delta_flag = True
                except:
                    pass

class ResultService:
    def __init__(self):
        self.formula_engine = FormulaEngine()
        self.delta_service = DeltaCheckService()

    async def save_batch(self, payload: ResultBatchUpdate) -> List[ResultRead]:
        # 1. Run Formulas
        processed_results = self.formula_engine.apply_formulas(payload.results)
        
        # 2. Save to DB (Mock Upsert)
        saved_objects = []
        for item in processed_results:
            # Check exist
            existing = next((r for r in MOCK_RESULTS if r.accession_id == payload.accession_id and r.parameter_slug == item.parameter_slug), None)
            
            if existing:
                existing.raw_value = item.raw_value
                existing.flag = item.flag
                existing.is_draft = not payload.final_submit
                existing.updated_at = datetime.now()
                obj = existing
            else:
                obj = ResultRead(
                    id=uuid4(), 
                    accession_id=payload.accession_id,
                    test_id=None,
                    unit="g/dL", # Mock default
                    is_draft=not payload.final_submit,
                    updated_at=datetime.now(),
                    **item.dict()
                )
                MOCK_RESULTS.append(obj)
            
            saved_objects.append(obj)

        # 3. Run Delta Checks on the way out
        # await self.delta_service.flag_deltas(mock_patient_id, saved_objects)
        
        return saved_objects

    async def get_results_by_accession(self, accession_id: UUID) -> List[ResultRead]:
        return [r for r in MOCK_RESULTS if str(r.accession_id) == str(accession_id)]

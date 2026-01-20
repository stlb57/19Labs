from uuid import UUID
from typing import List
from .schemas import PublicLabProfile, PublicCatalogItem, Badge

# --- Mock Data to simulate DB ---
MOCK_LABS = {
    "city-diagnostics": {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "name": "City Diagnostics Center",
        "description": "Leading pathology lab in Mumbai with NABL accreditation.",
        "address": "123, Health Street, Bandra West",
        "city": "Mumbai",
        "rating": 4.8,
        "review_count": 1240,
        "contact_phone": "+91 98765 43210"
    }
}

class MetricService:
    def get_badges_for_lab(self, lab_id: UUID) -> List[Badge]:
        """
        Calculates dynamic badges based on data.
        """
        # Logic: Query PostGIS for regional price. If lab_price < region_avg, add badge.
        return [
            Badge(
                id="best_price", 
                label="Best Price in 5km", 
                icon="Tag", 
                color="text-green-600",
                description="This lab offers the lowest price for CBC in your area."
            ),
            Badge(
                id="rapid_result", 
                label="6hr TAT Guarantee", 
                icon="Zap", 
                color="text-blue-600",
                description="Results delivered faster than 90% of labs."
            )
        ]

class ProfileService:
    def get_profile_by_slug(self, slug: str) -> PublicLabProfile:
        # 1. Fetch Lab Entity
        # lab = db.query(Lab).filter(slug=slug).first()
        raw_lab = MOCK_LABS.get(slug)
        if not raw_lab:
            return None # Handle 404 in route
            
        # 2. Fetch Catalog
        # catalog = db.query(Catalog).filter(lab_id=lab.id).all()
        # Mocking catalog
        catalog_items = [
            PublicCatalogItem(
                test_name="Complete Blood Count (CBC)",
                description="Measures red/white blood cells and platelets.",
                tat_hours=6,
                price=450.0,
                is_home_collection=True,
                department="Hematology",
                badges=[Badge(id="popular", label="Most Booked", icon="Star", color="text-yellow-600", description="")]
            ),
            PublicCatalogItem(
                test_name="Thyroid Profile (T3, T4, TSH)",
                description="Checks thyroid function metabolism.",
                tat_hours=12,
                price=800.0,
                is_home_collection=True,
                department="Biochemistry"
            )
        ]

        # 3. Aggregate
        badges = MetricService().get_badges_for_lab(UUID(raw_lab["id"]))
        
        return PublicLabProfile(
            id=UUID(raw_lab["id"]),
            name=raw_lab["name"],
            slug=slug,
            description=raw_lab["description"],
            address=raw_lab["address"],
            city=raw_lab["city"],
            rating=raw_lab["rating"],
            review_count=raw_lab["review_count"],
            contact_phone=raw_lab["contact_phone"],
            badges=badges,
            catalog=catalog_items
        )

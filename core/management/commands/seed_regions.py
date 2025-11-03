from django.core.management.base import BaseCommand
from core.models import Region


SAMPLES = [
    {
        "name": "Ludhiana",
        "state": "Punjab",
        "average_land_holding": 2.1,
        "land_holding": 2.3,
        "irrigation_type": "Tube Well",
        "dominant_crops": "Wheat, Rice",
        "rainfall": 700.0,
        "yield_per_hectare": 3.5,
        "irrigation_area": 1500.0,
        "latitude": 30.9010,
        "longitude": 75.8573,
    },
    {
        "name": "Pune",
        "state": "Maharashtra",
        "average_land_holding": 1.5,
        "land_holding": 1.4,
        "irrigation_type": "Canal",
        "dominant_crops": "Sugarcane, Wheat",
        "rainfall": 720.0,
        "yield_per_hectare": 2.9,
        "irrigation_area": 1200.0,
        "latitude": 18.5204,
        "longitude": 73.8567,
    },
    {
        "name": "Coimbatore",
        "state": "Tamil Nadu",
        "average_land_holding": 1.2,
        "land_holding": 1.1,
        "irrigation_type": "Drip",
        "dominant_crops": "Cotton, Coconut",
        "rainfall": 600.0,
        "yield_per_hectare": 3.1,
        "irrigation_area": 800.0,
        "latitude": 11.0168,
        "longitude": 76.9558,
    },
    {
        "name": "Lucknow",
        "state": "Uttar Pradesh",
        "average_land_holding": 1.0,
        "land_holding": 1.0,
        "irrigation_type": "Canal",
        "dominant_crops": "Rice, Wheat",
        "rainfall": 900.0,
        "yield_per_hectare": 2.7,
        "irrigation_area": 1100.0,
        "latitude": 26.8467,
        "longitude": 80.9462,
    },
    {
        "name": "Kolkata",
        "state": "West Bengal",
        "average_land_holding": 0.8,
        "land_holding": 0.9,
        "irrigation_type": "Well",
        "dominant_crops": "Rice, Jute",
        "rainfall": 1600.0,
        "yield_per_hectare": 2.5,
        "irrigation_area": 600.0,
        "latitude": 22.5726,
        "longitude": 88.3639,
    },
]


class Command(BaseCommand):
    help = "Seed sample Region data"

    def handle(self, *args, **options):
        created = 0
        for data in SAMPLES:
            obj, was_created = Region.objects.get_or_create(
                name=data["name"], state=data["state"], defaults=data
            )
            if was_created:
                created += 1
            else:
                # Update existing with latest defaults
                for k, v in data.items():
                    setattr(obj, k, v)
                obj.save()
        self.stdout.write(self.style.SUCCESS(f"Seed complete. Regions created/updated: {len(SAMPLES)} (new: {created})"))



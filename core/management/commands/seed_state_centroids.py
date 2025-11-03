from django.core.management.base import BaseCommand
from core.models import Region


# Approximate centroid coordinates for Indian States/UTs
STATE_CENTROIDS = {
    "Andhra Pradesh": (15.9129, 79.7400),
    "Arunachal Pradesh": (28.2180, 94.7278),
    "Assam": (26.2006, 92.9376),
    "Bihar": (25.0961, 85.3131),
    "Chhattisgarh": (21.2787, 81.8661),
    "Goa": (15.2993, 74.1240),
    "Gujarat": (22.2587, 71.1924),
    "Haryana": (29.0588, 76.0856),
    "Himachal Pradesh": (31.1048, 77.1734),
    "Jharkhand": (23.6102, 85.2799),
    "Karnataka": (15.3173, 75.7139),
    "Kerala": (10.8505, 76.2711),
    "Madhya Pradesh": (22.9734, 78.6569),
    "Maharashtra": (19.7515, 75.7139),
    "Manipur": (24.6637, 93.9063),
    "Meghalaya": (25.4670, 91.3662),
    "Mizoram": (23.1645, 92.9376),
    "Nagaland": (26.1584, 94.5624),
    "Odisha": (20.9517, 85.0985),
    "Punjab": (31.1471, 75.3412),
    "Rajasthan": (27.0238, 74.2179),
    "Sikkim": (27.5330, 88.5122),
    "Tamil Nadu": (11.1271, 78.6569),
    "Telangana": (18.1124, 79.0193),
    "Tripura": (23.9408, 91.9882),
    "Uttar Pradesh": (26.8467, 80.9462),
    "Uttarakhand": (30.0668, 79.0193),
    "West Bengal": (22.9868, 87.8550),
    # Union Territories / other entries in dataset
    "Andaman and Nicobar Islands": (11.7401, 92.6586),
    "Chandigarh": (30.7333, 76.7794),
    "Delhi": (28.6139, 77.2090),
    "Jammu and Kashmir": (33.7782, 76.5762),
    "Ladakh": (34.1526, 77.5770),
    "Lakshadweep": (10.5667, 72.6417),
    "Puducherry": (11.9416, 79.8083),
    "Dadra and Nagar Haveli and Daman and Diu": (20.3974, 72.8328),
}


class Command(BaseCommand):
    help = "Backfill latitude/longitude for Region entries using state/UT centroids"

    def handle(self, *args, **options):
        updated = 0
        for state, (lat, lon) in STATE_CENTROIDS.items():
            qs = Region.objects.filter(state__iexact=state)
            for region in qs:
                region.latitude = lat
                region.longitude = lon
                region.save()
                updated += 1
        self.stdout.write(self.style.SUCCESS(f"Updated coordinates for {updated} region records"))



from django.core.management.base import BaseCommand
from core.models import IrrigationArea
from core.management.commands.seed_state_centroids import STATE_CENTROIDS


class Command(BaseCommand):
    help = "Update coordinates for IrrigationArea entries using state centroids"

    def handle(self, *args, **options):
        updated = 0
        for state, (lat, lon) in STATE_CENTROIDS.items():
            # Try exact match first
            qs = IrrigationArea.objects.filter(state__iexact=state)
            if not qs.exists():
                # Try with different variations
                variations = [
                    state.replace("&", "and"),
                    state.replace("and", "&"),
                    state.upper(),
                    state.title()
                ]
                for variation in variations:
                    qs = IrrigationArea.objects.filter(state__iexact=variation)
                    if qs.exists():
                        break
            
            for area in qs:
                area.latitude = lat
                area.longitude = lon
                area.save()
                updated += 1
                self.stdout.write(f"Updated {area.state}: {lat}, {lon}")
        
        self.stdout.write(self.style.SUCCESS(f"Updated coordinates for {updated} irrigation areas"))

import json
import urllib.parse
import urllib.request
from typing import Dict, Any

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from core.models import Region


BASE_URL = (
    "https://api.data.gov.in/resource/89408984-6a8a-4510-82cc-7a7d39eaf799"
)


def fetch_records(api_key: str, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
    params = {
        "api-key": api_key,
        "format": "json",
        "limit": str(limit),
        "offset": str(offset),
    }
    url = f"{BASE_URL}?{urllib.parse.urlencode(params)}"
    with urllib.request.urlopen(url, timeout=30) as resp:
        if resp.status != 200:
            raise CommandError(f"HTTP {resp.status} from data.gov.in")
        data = json.loads(resp.read().decode("utf-8"))
        return data


class Command(BaseCommand):
    help = "Import state-wise land holdings from data.gov.in into Region (uses 2021-22 values)."

    def add_arguments(self, parser):
        parser.add_argument("--api-key", required=True, help="data.gov.in API key")
        parser.add_argument("--limit", type=int, default=100, help="Page size (default 100)")

    def handle(self, *args, **options):
        api_key = options.get("api_key")
        limit = options["limit"]

        # Fetch first page to get total
        first = fetch_records(api_key, limit=limit, offset=0)
        total = int(first.get("total", 0))
        records = list(first.get("records", []))

        # If more pages, fetch remaining
        offset = len(records)
        while offset < total:
            page = fetch_records(api_key, limit=limit, offset=offset)
            recs = page.get("records", [])
            if not recs:
                break
            records.extend(recs)
            offset += len(recs)

        if not records:
            raise CommandError("No records returned from data.gov.in")

        created, updated = 0, 0
        with transaction.atomic():
            for r in records:
                state = r.get("state_uts")
                latest = r.get("_2021_22")
                if not state:
                    # Skip invalid rows
                    continue
                try:
                    lh_val = float(latest) if latest is not None else None
                except (TypeError, ValueError):
                    lh_val = None

                # We model one Region per state when importing this dataset
                defaults = {
                    "name": state,
                    "average_land_holding": lh_val if lh_val is not None else 0.0,
                    "land_holding": lh_val,
                    "irrigation_type": "Unknown",
                    "dominant_crops": "",
                    "rainfall": 0.0,
                    "yield_per_hectare": 0.0,
                    "irrigation_area": None,
                    "latitude": None,
                    "longitude": None,
                }

                obj, was_created = Region.objects.get_or_create(
                    name=state,
                    state=state,
                    defaults=defaults,
                )
                if was_created:
                    created += 1
                else:
                    # Update land holding fields on existing record
                    obj.average_land_holding = defaults["average_land_holding"]
                    obj.land_holding = defaults["land_holding"]
                    obj.save()
                    updated += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Imported states: {len(records)}. Created: {created}. Updated: {updated}."
            )
        )



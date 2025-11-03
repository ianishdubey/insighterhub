import csv
from io import StringIO
from typing import Optional

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from core.models import Region

try:
    import requests  # optional; used when --url is provided
except Exception:  # pragma: no cover
    requests = None


FIELDS = [
    "name",
    "state",
    "average_land_holding",
    "land_holding",
    "irrigation_type",
    "dominant_crops",
    "rainfall",
    "yield_per_hectare",
    "irrigation_area",
    "latitude",
    "longitude",
]


class Command(BaseCommand):
    help = "Import Region rows from a CSV file or URL. Header must include the expected columns."

    def add_arguments(self, parser):
        parser.add_argument("--path", type=str, help="Path to local CSV file")
        parser.add_argument("--url", type=str, help="HTTP URL to CSV file")
        parser.add_argument("--update", action="store_true", help="Update existing rows as well")

    def handle(self, *args, **options):
        path = options.get("path")
        url = options.get("url")
        do_update = options.get("update")

        if not path and not url:
            raise CommandError("Provide --path or --url to a CSV")

        csv_text: Optional[str] = None
        if path:
            with open(path, "r", encoding="utf-8") as f:
                csv_text = f.read()
        else:
            if requests is None:
                raise CommandError("requests package not available; use --path or install requests")
            resp = requests.get(url, timeout=30)
            if resp.status_code != 200:
                raise CommandError(f"Failed to fetch CSV from URL: {resp.status_code}")
            csv_text = resp.text

        reader = csv.DictReader(StringIO(csv_text))
        missing = [c for c in ["name", "state"] if c not in reader.fieldnames]
        if missing:
            raise CommandError(f"CSV missing required columns: {', '.join(missing)}")

        count = 0
        created = 0
        with transaction.atomic():
            for row in reader:
                payload = {k: (row.get(k) if k in row else None) for k in FIELDS}

                # Convert numeric fields safely
                for num_key in [
                    "average_land_holding",
                    "land_holding",
                    "rainfall",
                    "yield_per_hectare",
                    "irrigation_area",
                    "latitude",
                    "longitude",
                ]:
                    val = payload.get(num_key)
                    if val is None or val == "":
                        payload[num_key] = None
                    else:
                        try:
                            payload[num_key] = float(val)
                        except ValueError:
                            raise CommandError(f"Invalid number for {num_key}: {val}")

                name = payload.pop("name")
                state = payload.pop("state")

                obj, was_created = Region.objects.get_or_create(
                    name=name, state=state, defaults=payload
                )
                if not was_created and do_update:
                    for k, v in payload.items():
                        setattr(obj, k, v)
                    obj.save()

                created += 1 if was_created else 0
                count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Imported {count} rows. Created: {created}. Updated: {count - created if do_update else 0}."
            )
        )



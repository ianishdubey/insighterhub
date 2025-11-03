import json
from typing import Any, Dict, List, Optional

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from core.models import IrrigationArea
from core.management.commands.seed_state_centroids import STATE_CENTROIDS


def to_float(value: Optional[str]) -> Optional[float]:
    if value is None:
        return None
    s = str(value).strip()
    if s in ("", "NA", "N/A", "NaN", "nan"):
        return None
    try:
        return float(s)
    except ValueError:
        return None


class Command(BaseCommand):
    help = "Import irrigation area statistics from a JSON payload/file matching the provided schema."

    def add_arguments(self, parser):
        parser.add_argument("--path", type=str, help="Path to JSON file; if omitted, reads from stdin")

    def handle(self, *args, **options):
        path = options.get("path")
        if path:
            with open(path, "r", encoding="utf-8") as f:
                payload = json.load(f)
        else:
            try:
                payload = json.load(self.stdin)
            except Exception as exc:
                raise CommandError(f"Failed to read JSON from stdin: {exc}")

        fields: List[Dict[str, Any]] = payload.get("fields") or []
        data: List[List[Any]] = payload.get("data") or []
        if not fields or not data:
            raise CommandError("JSON must include 'fields' and 'data'")

        # Map labels to column indices for robust access
        label_to_index: Dict[str, int] = {f["label"]: idx for idx, f in enumerate(fields)}

        required_labels = [
            "State",
            "Actual area irrigated (Ha) - Kharif",
            "Actual area irrigated (Ha) - Rabi", 
            "Actual area irrigated (Ha) - Perennial",
            "Actual area irrigated (Ha) - Others",
            "Total"
        ]
        missing = [lab for lab in required_labels if lab not in label_to_index]
        if missing:
            raise CommandError(f"Missing required labels: {', '.join(missing)}")

        created = 0
        updated = 0
        with transaction.atomic():
            for row in data:
                state = row[label_to_index["State"]]

                defaults = {
                    "kharif_area": to_float(row[label_to_index["Actual area irrigated (Ha) - Kharif"]]),
                    "rabi_area": to_float(row[label_to_index["Actual area irrigated (Ha) - Rabi"]]),
                    "perennial_area": to_float(row[label_to_index["Actual area irrigated (Ha) - Perennial"]]),
                    "others_area": to_float(row[label_to_index["Actual area irrigated (Ha) - Others"]]),
                    "total_area": to_float(row[label_to_index["Total"]]),
                }

                # Set coordinates from centroid helper if available
                coords = STATE_CENTROIDS.get(state) or STATE_CENTROIDS.get(state.replace("&", "and"))
                if coords:
                    defaults["latitude"], defaults["longitude"] = coords

                obj, was_created = IrrigationArea.objects.get_or_create(
                    state=state, defaults=defaults
                )
                if not was_created:
                    for k, v in defaults.items():
                        setattr(obj, k, v)
                    obj.save()
                    updated += 1
                else:
                    created += 1

        self.stdout.write(self.style.SUCCESS(
            f"Imported {created + updated} IrrigationArea rows (created: {created}, updated: {updated})."
        ))

import json
from typing import Any, Dict, List, Optional

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from core.models import CroppingStat
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
    help = "Import cropping land-use statistics from a JSON payload/file matching the provided schema."

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
            "States/UTs", "Category", "Total geographical area",
            "Reporting area for land utilization", "Forests",
            "Not available for cultivation",
            "Permanent pastures and other grazing lands",
            "Land under miscellaneous tree crops & groves",
            "Culturable wasteland",
            "Fallow lands other than current fallows",
            "Current fallows",
            "Net area sown",
        ]
        missing = [lab for lab in required_labels if lab not in label_to_index]
        if missing:
            raise CommandError(f"Missing required labels: {', '.join(missing)}")

        created = 0
        updated = 0
        with transaction.atomic():
            for row in data:
                state = row[label_to_index["States/UTs"]]
                category = row[label_to_index["Category"]]

                defaults = {
                    "total_geographical_area": to_float(row[label_to_index["Total geographical area"]]),
                    "reporting_area": to_float(row[label_to_index["Reporting area for land utilization"]]),
                    "forests": to_float(row[label_to_index["Forests"]]),
                    "not_available_for_cultivation": to_float(row[label_to_index["Not available for cultivation"]]),
                    "permanent_pastures": to_float(row[label_to_index["Permanent pastures and other grazing lands"]]),
                    "tree_crops_and_groves": to_float(row[label_to_index["Land under miscellaneous tree crops & groves"]]),
                    "culturable_wasteland": to_float(row[label_to_index["Culturable wasteland"]]),
                    "fallow_other_than_current": to_float(row[label_to_index["Fallow lands other than current fallows"]]),
                    "current_fallows": to_float(row[label_to_index["Current fallows"]]),
                    "net_area_sown": to_float(row[label_to_index["Net area sown"]]),
                }

                # Set coordinates from centroid helper if available
                coords = STATE_CENTROIDS.get(state) or STATE_CENTROIDS.get(state.replace("&", "and"))
                if coords:
                    defaults["latitude"], defaults["longitude"] = coords

                obj, was_created = CroppingStat.objects.get_or_create(
                    state=state, category=category, defaults=defaults
                )
                if not was_created:
                    for k, v in defaults.items():
                        setattr(obj, k, v)
                    obj.save()
                    updated += 1
                else:
                    created += 1

        self.stdout.write(self.style.SUCCESS(
            f"Imported {created + updated} CroppingStat rows (created: {created}, updated: {updated})."
        ))



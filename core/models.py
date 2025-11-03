from django.db import models

class Region(models.Model):
    name = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    average_land_holding = models.FloatField()
    # New normalized fields for analytics/UI
    land_holding = models.FloatField(null=True, blank=True)
    irrigation_area = models.FloatField(null=True, blank=True)
    irrigation_type = models.CharField(max_length=100)
    dominant_crops = models.CharField(max_length=200)
    rainfall = models.FloatField()
    yield_per_hectare = models.FloatField()
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.name


class CroppingStat(models.Model):
    state = models.CharField(max_length=100)
    category = models.CharField(max_length=100)  # e.g., "Area" or "Percentage to Geographical Area"

    total_geographical_area = models.FloatField(null=True, blank=True)
    reporting_area = models.FloatField(null=True, blank=True)
    forests = models.FloatField(null=True, blank=True)
    not_available_for_cultivation = models.FloatField(null=True, blank=True)
    permanent_pastures = models.FloatField(null=True, blank=True)
    tree_crops_and_groves = models.FloatField(null=True, blank=True)
    culturable_wasteland = models.FloatField(null=True, blank=True)
    fallow_other_than_current = models.FloatField(null=True, blank=True)
    current_fallows = models.FloatField(null=True, blank=True)
    net_area_sown = models.FloatField(null=True, blank=True)

    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.state} - {self.category}"


class IrrigationArea(models.Model):
    state = models.CharField(max_length=100)
    kharif_area = models.FloatField(null=True, blank=True)  # Actual area irrigated (Ha) - Kharif
    rabi_area = models.FloatField(null=True, blank=True)   # Actual area irrigated (Ha) - Rabi
    perennial_area = models.FloatField(null=True, blank=True)  # Actual area irrigated (Ha) - Perennial
    others_area = models.FloatField(null=True, blank=True)  # Actual area irrigated (Ha) - Others
    total_area = models.FloatField(null=True, blank=True)   # Total

    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.state} - Irrigation Areas"


class GalleryItem(models.Model):
    CATEGORY_CHOICES = [
        ("holding", "Land Holding"),
        ("irrigation", "Irrigation"),
        ("cropping", "Cropping"),
    ]

    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    image = models.FileField(upload_to='gallery/')
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_category_display()} - {self.id}"
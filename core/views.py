from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_http_methods
from .models import Region, CroppingStat, IrrigationArea, GalleryItem
from django.contrib.auth.models import User
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Avg, Min, Max, Count, F
from django.db.models.functions import Coalesce
from .models import Region, CroppingStat, IrrigationArea
from .serializers import RegionSerializer, CroppingStatSerializer, IrrigationAreaSerializer
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login

class RegionViewSet(viewsets.ModelViewSet):
    queryset = Region.objects.all()
    serializer_class = RegionSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = []  # Explicitly disable auth for this viewset

    def get_queryset(self):
        qs = super().get_queryset()
        params = self.request.query_params

        state = params.get("state")
        irrigation_type = params.get("irrigation_type")
        crop = params.get("crop")  # matches against dominant_crops icontains
        lh_min = params.get("land_holding_min")
        lh_max = params.get("land_holding_max")
        ia_min = params.get("irrigation_area_min")
        ia_max = params.get("irrigation_area_max")
        rain_min = params.get("rainfall_min")
        rain_max = params.get("rainfall_max")

        if state:
            qs = qs.filter(state__iexact=state)
        if irrigation_type:
            qs = qs.filter(irrigation_type__iexact=irrigation_type)
        if crop:
            qs = qs.filter(dominant_crops__icontains=crop)

        # Effective land holding fallback
        qs = qs.annotate(effective_land_holding=Coalesce(F("land_holding"), F("average_land_holding")))
        if lh_min is not None:
            qs = qs.filter(effective_land_holding__gte=lh_min)
        if lh_max is not None:
            qs = qs.filter(effective_land_holding__lte=lh_max)

        if ia_min is not None:
            qs = qs.filter(irrigation_area__gte=ia_min)
        if ia_max is not None:
            qs = qs.filter(irrigation_area__lte=ia_max)

        if rain_min is not None:
            qs = qs.filter(rainfall__gte=rain_min)
        if rain_max is not None:
            qs = qs.filter(rainfall__lte=rain_max)

        return qs

    @action(detail=False, methods=["get"], url_path="summary", permission_classes=[permissions.AllowAny])
    def summary(self, request):
        qs = self.get_queryset()

        aggregates = qs.aggregate(
            count=Count("id"),
            avg_land_holding=Avg("land_holding"),
            avg_land_holding_legacy=Avg("average_land_holding"),
            min_land_holding=Min("land_holding"),
            max_land_holding=Max("land_holding"),
            total_irrigation_area=Avg("irrigation_area"),
            avg_rainfall=Avg("rainfall"),
        )

        # Use legacy average if new is null
        if aggregates["avg_land_holding"] is None:
            aggregates["avg_land_holding"] = aggregates["avg_land_holding_legacy"]
        aggregates.pop("avg_land_holding_legacy", None)

        # Most common irrigation type
        top_irrigation = (
            qs.values("irrigation_type").annotate(c=Count("id")).order_by("-c").first()
        )

        # Top crops from comma-separated dominant_crops
        crop_counts = {}
        for item in qs.values_list("dominant_crops", flat=True):
            if not item:
                continue
            for c in [x.strip() for x in item.split(",") if x.strip()]:
                crop_counts[c] = crop_counts.get(c, 0) + 1
        top_crops = sorted(crop_counts.items(), key=lambda x: x[1], reverse=True)[:5]

        return Response({
            "count": aggregates.get("count") or 0,
            "avg_land_holding": aggregates.get("avg_land_holding"),
            "min_land_holding": aggregates.get("min_land_holding"),
            "max_land_holding": aggregates.get("max_land_holding"),
            "avg_rainfall": aggregates.get("avg_rainfall"),
            "total_irrigation_area": aggregates.get("total_irrigation_area"),
            "top_irrigation_type": top_irrigation["irrigation_type"] if top_irrigation else None,
            "top_crops": [c for c, _ in top_crops],
        })


class UserRegistrationView(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]
    
    def create(self, request):
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')
        
        if not all([username, email, password]):
            return Response(
                {"detail": "Username, email, and password are required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if User.objects.filter(username=username).exists():
            return Response(
                {"detail": "Username already exists"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if User.objects.filter(email=email).exists():
            return Response(
                {"detail": "Email already exists"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        
        return Response(
            {"detail": "User created successfully"}, 
            status=status.HTTP_201_CREATED
        )


@login_required(login_url='/login/')
def index(request):
    return render(request, 'index.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})
    return render(request, 'login.html')

def holding_view(request):
    return render(request, 'holding.html')

def irrigation_view(request):
    return render(request, 'irrigation.html')

def cropping_view(request):
    return render(request, 'cropping.html')

def signup_view(request):
    return render(request, 'signup.html')

def logout_view(request):
    logout(request)
    return redirect('login')


class CroppingStatViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CroppingStat.objects.all()
    serializer_class = CroppingStatSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def get_queryset(self):
        qs = super().get_queryset()
        params = self.request.query_params
        state = params.get('state')
        category = params.get('category')
        if state:
            qs = qs.filter(state__iexact=state)
        if category:
            qs = qs.filter(category__iexact=category)
        return qs


class IrrigationAreaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = IrrigationArea.objects.all()
    serializer_class = IrrigationAreaSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def get_queryset(self):
        qs = super().get_queryset()
        params = self.request.query_params
        state = params.get('state')
        if state:
            qs = qs.filter(state__iexact=state)
        return qs


# --------- Gallery Pages ---------
CATEGORY_TO_TITLE = {
    "holding": "Land Holding Gallery",
    "irrigation": "Irrigation Gallery",
    "cropping": "Cropping Gallery",
}


def gallery_view(request, category: str):
    if category not in CATEGORY_TO_TITLE:
        return redirect('index')
    items = GalleryItem.objects.filter(category=category).order_by('-created_at')
    select_mode = request.GET.get('select') == '1'
    return render(request, 'gallery.html', {
        'title': CATEGORY_TO_TITLE[category],
        'items': items,
        'category': category,
        'select_mode': select_mode,
    })


@staff_member_required
@require_http_methods(["GET", "POST"])
def gallery_upload(request, category: str):
    if category not in CATEGORY_TO_TITLE:
        return redirect('index')
    if request.method == 'POST':
        image = request.FILES.get('image')
        description = request.POST.get('description', '')
        if image:
            GalleryItem.objects.create(category=category, image=image, description=description)
            return redirect('gallery', category=category)
        # No image provided — re-render with an error message
        return render(request, 'gallery_upload.html', {
            'title': f"Add Item - {CATEGORY_TO_TITLE[category]}",
            'category': category,
            'error': 'Please choose an image before saving.'
        })
    return render(request, 'gallery_upload.html', {
        'title': f"Add Item - {CATEGORY_TO_TITLE[category]}",
        'category': category,
    })


@staff_member_required
@require_http_methods(["POST"]) 
def gallery_delete(request, category: str, item_id: int):
    if category not in CATEGORY_TO_TITLE:
        return redirect('index')
    try:
        item = GalleryItem.objects.get(id=item_id, category=category)
        item.delete()
    except GalleryItem.DoesNotExist:
        pass
    return redirect('gallery', category=category)


@staff_member_required
@require_http_methods(["POST"])
def gallery_bulk_delete(request, category: str):
    if category not in CATEGORY_TO_TITLE:
        return redirect('index')
    ids = request.POST.getlist('ids')
    if ids:
        GalleryItem.objects.filter(category=category, id__in=ids).delete()
    return redirect('gallery', category=category)


@staff_member_required
@require_http_methods(["GET", "POST"])
def gallery_edit(request, category: str, item_id: int):
    if category not in CATEGORY_TO_TITLE:
        return redirect('index')
    try:
        item = GalleryItem.objects.get(id=item_id, category=category)
    except GalleryItem.DoesNotExist:
        return redirect('gallery', category=category)

    if request.method == 'POST':
        description = request.POST.get('description', '')
        image = request.FILES.get('image')
        item.description = description
        if image:
            item.image = image
        item.save()
        return redirect('gallery', category=category)

    return render(request, 'gallery_edit.html', {
        'title': f"Edit Item - {CATEGORY_TO_TITLE[category]}",
        'category': category,
        'item': item,
    })


@staff_member_required
@require_http_methods(["POST"])
def gallery_bulk_edit_redirect(request, category: str):
    if category not in CATEGORY_TO_TITLE:
        return redirect('index')
    ids = request.POST.getlist('ids')
    if len(ids) == 1:
        return redirect('gallery_edit', category=category, item_id=ids[0])
    # If zero or multiple selected, stay in select mode
    return redirect(f'/{category}/gallery/?select=1')

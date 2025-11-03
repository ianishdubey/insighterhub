from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RegionViewSet, UserRegistrationView, CroppingStatViewSet, IrrigationAreaViewSet

router = DefaultRouter()
router.register('regions', RegionViewSet, basename='region')
router.register('register', UserRegistrationView, basename='register')
router.register('cropping-stats', CroppingStatViewSet, basename='croppingstat')
router.register('irrigation-areas', IrrigationAreaViewSet, basename='irrigationarea')

urlpatterns = [
    path('', include(router.urls)),
]

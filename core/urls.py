from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import index, login_view, holding_view, irrigation_view, cropping_view, signup_view, gallery_view, gallery_upload, gallery_delete, gallery_bulk_delete, gallery_edit, gallery_bulk_edit_redirect, logout_view

urlpatterns = [
    # Frontend pages
    path('', index, name='index'),
    path('login/', login_view, name='login'),
    path('holding/', holding_view, name='holding'),
    path('irrigation/', irrigation_view, name='irrigation'),
    path('cropping/', cropping_view, name='cropping'),
    path('signup/', signup_view, name='signup'),
    path('logout/', logout_view, name='logout'),

    # Gallery pages
    path('<str:category>/gallery/', gallery_view, name='gallery'),
    path('<str:category>/gallery/upload/', gallery_upload, name='gallery_upload'),
    path('<str:category>/gallery/<int:item_id>/delete/', gallery_delete, name='gallery_delete'),
    path('<str:category>/gallery/bulk-delete/', gallery_bulk_delete, name='gallery_bulk_delete'),
    path('<str:category>/gallery/<int:item_id>/edit/', gallery_edit, name='gallery_edit'),
    path('<str:category>/gallery/bulk-edit/', gallery_bulk_edit_redirect, name='gallery_bulk_edit'),

    # ✅ JWT Authentication endpoints still under /api/
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

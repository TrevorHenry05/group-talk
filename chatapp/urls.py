from django.urls import path, include
from .views.user_views import RegisterView, LoginView, UserViewSet
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

"""
Endpoints for:
    List users: GET /api/users
    Get user: GET /api/users/{id}
    Update user: PUT /api/users/{id}
    Delete user: DELETE /api/users/{id} 
"""
router.register('users', UserViewSet)

urlpatterns = [
    path('register', RegisterView.as_view(), name='register'),
    path('login', LoginView.as_view(), name='login'),
    path('token/refresh', TokenRefreshView.as_view(), name="token_refresh"),
    path('', include(router.urls))
]

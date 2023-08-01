from django.urls import path
from .views import (
    CustomTokenObtainPairView,
    CustomTokenRefreshView,
    CustomTokenVerifyView,
    LogoutView,
    CustomUserViewSet,
    CurrentUserView
)
urlpatterns = [
    path("jwt/create/", CustomTokenObtainPairView.as_view()),
    path("jwt/refresh/", CustomTokenRefreshView.as_view()),
    path("jwt/verify/", CustomTokenVerifyView.as_view()),
    path("logout/", LogoutView.as_view()),
    path("users_api/", CustomUserViewSet.as_view({"post": "create"}),
          name="user-registration"),
    path("current_user/", CurrentUserView.as_view(), name="user-current"),   
]

from django.urls import path # define URL routes in Django
from .views import RegisterView, LoginView, AdminProtectedView, AdminView, ManagerView, UserView, LogoutView # Imports registerview and loginview so that we can access them
from authentication.views import ProtectedView
from rest_framework_simplejwt.views import TokenRefreshView


urlpatterns = [ # url / function we wrote earlier and then the name we use internally
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("api/protected/", ProtectedView.as_view(), name="protected"),
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"), 
    path("api/admin/protected/", AdminProtectedView.as_view(), name="admin-protected"),
    path("admin-only/", AdminView.as_view(), name="admin-only"),
    path("manager-only/", ManagerView.as_view(), name="manager-only"),
    path("user-only/", UserView.as_view(), name="user-only"),
    path("logout/", LogoutView.as_view(), name="logout"),
]
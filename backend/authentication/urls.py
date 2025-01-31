from django.urls import path # define URL routes in Django
from .views import RegisterView, LoginView # Imports registerview and loginview so that we can access them
from authentication.views import ProtectedView

urlpatterns = [ # url / function we wrote earlier and then the name we use internally
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("api/protected/", ProtectedView.as_view(), name="protected"),
]
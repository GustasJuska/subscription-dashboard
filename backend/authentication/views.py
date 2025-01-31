from rest_framework.views import APIView # Uses APIView to create API endpoints
from rest_framework.response import Response # Uses Response to send JSON responses
from rest_framework.permissions import AllowAny # - to make certain routes public
from rest_framework_simplejwt.tokens import RefreshToken # to genetrate JWT tokens
from django.contrib.auth import get_user_model, authenticate # verify credentials
from django.shortcuts import render

# Create your views here.
User = get_user_model()

class RegisterView(APIView): #Creates the APi for registering
    permission_classes = [AllowAny]

    def post(self, request): # accepts POST request with email, username and password
        email = request.data.get("email")
        username = request.data.get("username")
        password = request.data.get("password")

        if User.objects.filter(email=email).exists(): #checks email exists
            return Response({"error": "Email already exists"}, status=400)

        user = User.objects.create_user(email=email, username=username, password=password) # creates a new user if the email is unique
        return Response({"message": "User registered successfully"})

class LoginView(APIView): # Creates the api for login
    permission_classes = [AllowAny] # Means anyone can access it even when not logged in

    def post(self, request): # reads the request
        email = request.data.get("email") # extracts email entered by user
        password = request.data.get("password")
        user = authenticate(username=email, password=password) # checks if the email and password match a real user in the database

        if user is not None: # checks if user exists and if they do then django generates a JWT refresh and access token so that the user can access the protected API requests
            refresh = RefreshToken.for_user(user)
            return Response({
                "refresh": str(refresh), #Refreshes the token every 15 minutes so that If a token is stolen then it expires quickly
                "access": str(refresh.access_token)
            })
        return Response({"error": "Invalid Credentials"}, status=400)
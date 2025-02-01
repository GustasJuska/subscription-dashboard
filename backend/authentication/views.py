from rest_framework.views import APIView # Uses APIView to create API endpoints
from rest_framework.response import Response # Uses Response to send JSON responses
from rest_framework.permissions import AllowAny, IsAuthenticated, BasePermission # - to make certain routes public
from rest_framework_simplejwt.tokens import RefreshToken # to genetrate JWT tokens
from django.contrib.auth import get_user_model, authenticate # verify credentials
from .permissions import IsAdmin, IsManager, IsUser # Imported functions from permissions
from django.shortcuts import render
from rest_framework import status
from django.conf import settings
import stripe

# Create your views here.
User = get_user_model()
stripe.api_key = settings.STRIPE_SECRET_KEY

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
        user = authenticate(email=email, password=password) # checks if the email and password match a real user in the database

        if user is not None: # checks if user exists and if they do then django generates a JWT refresh and access token so that the user can access the protected API requests
            refresh = RefreshToken.for_user(user)
            return Response({
                "refresh": str(refresh), #Refreshes the token every 15 minutes so that If a token is stolen then it expires quickly
                "access": str(refresh.access_token)
            })
        return Response({"error": "Invalid Credentials"}, status=400)

class ProtectedView(APIView):
    permission_classes = [IsAuthenticated]  # Requires login, can only access this with the JWT token

    def get(self, request):
        return Response({"message": "You are authenticated!"})

class IsAdmin(BasePermission):
    """ Custom permission to allow only admins """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'

class AdminProtectedView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        return Response({"message": "You are an admin!"})

class AdminView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        return Response({"dashboard": "Admin panel data here"})

class ManagerView(APIView):
    permission_classes = [IsAuthenticated, IsManager]

    def get(self, request):
        return Response({"message": "You are a manager!"})

class UserView(APIView):
    permission_classes = [IsAuthenticated, IsUser]

    def get(self, request):
        return Response({"message": "You are a user!"})

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()  # This blacklists the token
            return Response({"message": "Successfully logged out"}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)

class CreateSubscriptionView(APIView):
    permission_classes = [IsAuthenticated]

    def attach_payment_method_to_customer(self, customer_id, payment_method_id):
        """
        Attaches a payment method to a Stripe customer and sets it as the default.
        """
        try:
            # Attach the payment method to the customer
            attached_payment_method = stripe.PaymentMethod.attach(
                payment_method_id,
                customer=customer_id,
            )
            
            # Update the customer to set the attached payment method as the default
            stripe.Customer.modify(
                customer_id,
                invoice_settings={"default_payment_method": payment_method_id},
            )
            return attached_payment_method
        except stripe.error.StripeError as e:
            # Handle the error accordingly (e.g., log the error, return error response)
            raise e

    def create_subscription(self, customer_id, payment_method_id, plan_id):
        # First, ensure that the payment method is attached to the customer
        self.attach_payment_method_to_customer(customer_id, payment_method_id)
        
        # Now, create the subscription post attaching the payment method
        subscription = stripe.Subscription.create(
            customer=customer_id,
            items=[{"plan": plan_id}],
            expand=["latest_invoice.payment_intent"],
        )
        return subscription

    def post(self, request):
        user = request.user
        plan = request.data.get("plan", "basic")
        payment_method_id = request.data.get("payment_method_id")

        # Check if user already has a subscription
        if Subscription.objects.filter(user=user, is_active=True).exists():
            return Response({"error": "User already has an active subscription."}, status=400)

        # Create a Stripe Customer
        customer = stripe.Customer.create(email=user.email)

        # Create the subscription
        try:
            subscription = self.create_subscription(customer.id, payment_method_id, plan)
            # Save Subscription in DB
            Subscription.objects.create(
                user=user,
                stripe_customer_id=customer.id,
                stripe_subscription_id=subscription.id,
                plan=plan,
                is_active=True
            )
            return Response({"message": "Subscription created successfully", "subscription_id": subscription.id})
        except stripe.error.StripeError as e:
            return Response({"error": str(e)}, status=400)
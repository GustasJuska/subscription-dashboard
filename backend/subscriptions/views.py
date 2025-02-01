from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
import stripe
from subscriptions.models import Subscription

stripe.api_key = settings.STRIPE_SECRET_KEY

class CreateSubscriptionView(APIView):
    permission_classes = [IsAuthenticated]

    def attach_payment_method_to_customer(self, customer_id, payment_method_id):
        """
        Attaches a payment method to a Stripe customer only if it's not already attached.
        """
        try:
            # Retrieve the payment method
            payment_method = stripe.PaymentMethod.retrieve(payment_method_id)

            # Check if it's already attached to a customer
            if payment_method.customer:
                print(f"✅ Payment method {payment_method_id} is already attached to a customer.")
            else:
                stripe.PaymentMethod.attach(payment_method_id, customer=customer_id)
                print(f"✅ Successfully attached payment method {payment_method_id} to customer {customer_id}")

            # Always set it as the default payment method
            stripe.Customer.modify(
                customer_id,
                invoice_settings={"default_payment_method": payment_method_id},
            )

            return payment_method

        except stripe.error.StripeError as e:
            raise e  # Handle errors if needed


    def create_subscription(self, customer_id, payment_method_id, price_id):
        """
        Creates a new Stripe subscription using a valid Price ID.
        """
        # Attach payment method before creating the subscription
        self.attach_payment_method_to_customer(customer_id, payment_method_id)
        
        # Create the subscription with correct Price ID
        subscription = stripe.Subscription.create(
            customer=customer_id,
            items=[{"price": price_id}],  # ✅ Use "price" instead of "plan"
            expand=["latest_invoice.payment_intent"],
        )
        return subscription

    def post(self, request):
        user = request.user
        price_id = request.data.get("price_id")  # ✅ Updated to use "price_id"

        if not price_id:
            return Response({"error": "Price ID is required."}, status=400)

        payment_method_id = request.data.get("payment_method_id")

        if not payment_method_id:
            return Response({"error": "Payment Method ID is required."}, status=400)

        # Check if user already has an active subscription
        if Subscription.objects.filter(user=user, is_active=True).exists():
            return Response({"error": "User already has an active subscription."}, status=400)

        # Check if the user already has a Stripe customer
        existing_customers = stripe.Customer.list(email=user.email).data

        if existing_customers:
            customer = existing_customers[0]  # ✅ Use existing customer
            print(f"✅ Using existing Stripe customer: {customer.id}")
        else:
            customer = stripe.Customer.create(email=user.email)
            print(f"✅ Created new Stripe customer: {customer.id}")

        # Create the subscription
        try:
            subscription = self.create_subscription(customer.id, payment_method_id, price_id)
            
            # Save Subscription in Database
            Subscription.objects.create(
                user=user,
                stripe_customer_id=customer.id,
                stripe_subscription_id=subscription.id,
                plan=price_id,  # ✅ Save "price_id" instead of "plan"
                is_active=True
            )
            return Response({"message": "Subscription created successfully", "subscription_id": subscription.id})
        except stripe.error.StripeError as e:
            return Response({"error": str(e)}, status=400)

    @csrf_exempt
    def stripe_webhook(request):
        payload = request.body
        sig_header = request.headers.get('Stripe-Signature')
        endpoint_secret = "your_webhook_secret"

        try:
            event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
        except ValueError as e:
            return JsonResponse({'error': str(e)}, status=400)
        except stripe.error.SignatureVerificationError as e:
            return JsonResponse({'error': 'Invalid signature'}, status=400)

        if event['type'] == 'invoice.payment_succeeded':
            subscription_id = event['data']['object']['subscription']
            print(f"✅ Payment received for subscription {subscription_id}")
            # Update database (mark subscription as active)

        elif event['type'] == 'invoice.payment_failed':
            subscription_id = event['data']['object']['subscription']
            print(f"❌ Payment failed for subscription {subscription_id}")
            # Update database (mark subscription as unpaid)

        elif event['type'] == 'customer.subscription.deleted':
            subscription_id = event['data']['object']['id']
            print(f"🔴 Subscription {subscription_id} canceled.")
            # Update database (mark subscription as canceled)

        return JsonResponse({'status': 'success'}, status=200)

class GetSubscriptionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        try:
            subscription = Subscription.objects.get(user=user, is_active=True)
            return Response({
                "subscription_id": subscription.stripe_subscription_id,
                "plan": subscription.plan,
                "status": "Active"
            })
        except Subscription.DoesNotExist:
            return Response({"error": "No active subscription found."}, status=404)    

class CancelSubscriptionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        try:
            subscription = Subscription.objects.get(user=user, is_active=True)
            stripe.Subscription.delete(subscription.stripe_subscription_id)
            subscription.is_active = False
            subscription.save()
            return Response({"message": "Subscription canceled successfully."})
        except Subscription.DoesNotExist:
            return Response({"error": "No active subscription found."}, status=404)
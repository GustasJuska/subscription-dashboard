from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
import stripe
from subscriptions.models import Subscription
from django.shortcuts import get_object_or_404


stripe.api_key = settings.STRIPE_SECRET_KEY

class CreateSubscriptionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        plan = request.data.get("plan")

        price_id_mapping = settings.STRIPE_PRICE_IDS
        price_id = price_id_mapping.get(plan)  # ✅ Get correct Stripe price ID

        if not plan:
            return Response({"error": "Plan is required."}, status=400)

        # Check if user already has an active subscription
        if Subscription.objects.filter(user=user, is_active=True).exists():
            return Response({"error": "User already has an active subscription."}, status=400)

        existing_customers = stripe.Customer.list(email=user.email).data

        if existing_customers:
            customer = existing_customers[0]  # ✅ Use existing customer
            print(f"✅ Using existing Stripe customer: {customer.id}")
        else:
            customer = stripe.Customer.create(email=user.email)
            print(f"✅ Created new Stripe customer: {customer.id}")

        if not customer or not hasattr(customer, "id"):
            return Response({"error": "Stripe customer creation failed."}, status=400)

        # ✅ Handle Free Plan (Basic)
        if plan == "basic":
            try:
                Subscription.objects.create(
                    user=user,
                    stripe_customer_id=customer.id,
                    stripe_subscription_id=None,  # ✅ No Stripe Subscription needed for free plan
                    plan="Basic",
                    is_active=True
                )
                return Response({
                    "message": "Basic plan activated successfully.",
                    "subscription_id": None,  # ✅ No Stripe Subscription for free plan
                    "plan": "Basic",
                    "checkout_url": None  # ✅ No checkout required
                })
            except Exception as e:
                return Response({"error": str(e)}, status=400)

        # ✅ Handle Paid Plans (Pro, Enterprise)
        if plan in ["pro", "enterprise"]:
            if not price_id:
                return Response({"error": "Invalid plan selected."}, status=400)

            # Create Stripe Checkout Session
            try:
                checkout_session = stripe.checkout.Session.create(
                    payment_method_types=["card"],
                    customer_email=user.email,  # Stripe will link it to this user
                    line_items=[{"price": price_id, "quantity": 1}],
                    mode="subscription",
                    success_url="http://localhost:3000/dashboard?session_id={CHECKOUT_SESSION_ID}",  # ✅ Redirect on success
                    cancel_url="http://localhost:3000/pricing",  # ✅ Redirect if canceled
                )

                return Response({
                    "checkout_url": checkout_session.url  # ✅ Send URL to frontend
                })

            except stripe.error.StripeError as e:
                return Response({"error": str(e)}, status=400)

        return Response({"error": "Invalid plan type."}, status=400)

    @csrf_exempt
    def stripe_webhook(request):
        payload = request.body
        sig_header = request.headers.get("Stripe-Signature")
        endpoint_secret = "your_webhook_secret"

        try:
            event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
        except ValueError as e:
            return JsonResponse({"error": str(e)}, status=400)
        except stripe.error.SignatureVerificationError as e:
            return JsonResponse({"error": "Invalid signature"}, status=400)

        if event["type"] == "invoice.payment_succeeded":
            subscription_id = event["data"]["object"]["subscription"]
            print(f"✅ Payment received for subscription {subscription_id}")
            
            # ✅ Update subscription in the database
            subscription = get_object_or_404(Subscription, stripe_subscription_id=subscription_id)
            subscription.is_active = True
            subscription.save()

        elif event["type"] == "invoice.payment_failed":
            subscription_id = event["data"]["object"]["subscription"]
            print(f"⚠️ Payment failed for subscription {subscription_id}")

            # ❌ Mark subscription as unpaid
            subscription = get_object_or_404(Subscription, stripe_subscription_id=subscription_id)
            subscription.is_active = False
            subscription.save()

        elif event["type"] == "customer.subscription.deleted":
            subscription_id = event["data"]["object"]["id"]
            print(f"❌ Subscription {subscription_id} canceled.")

            # 🚨 Mark subscription as canceled
            subscription = get_object_or_404(Subscription, stripe_subscription_id=subscription_id)
            subscription.is_active = False
            subscription.save()

        return JsonResponse({"status": "success"}, status=200)

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

class UpgradeSubscriptionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        new_price_id = request.data.get("price_id")  # e.g., "pro" or "enterprise"

        if not new_price_id:
            return Response({"error": "Invalid plan choice."}, status=400)

        try:
            subscription = Subscription.objects.get(user=user, is_active=True)
            price = stripe.Price.retrieve(new_price_id)
            product = stripe.Product.retrieve(price["product"])
            new_plan_name = product["name"]  # ✅ Get new plan name dynamically

            # ✅ Update subscription in Stripe
            stripe.Subscription.modify(
                subscription.stripe_subscription_id,
                items=[{"price": new_price_id}]
            )

            # ✅ Update subscription in the database
            subscription.plan = new_plan_name
            subscription.save()

            return Response({"message": f"Subscription upgraded to {new_plan_name} successfully."})
        except Subscription.DoesNotExist:
            return Response({"error": "No active subscription found."}, status=404)
        except stripe.error.StripeError as e:
            return Response({"error": f"Stripe error: {str(e)}"}, status=400)

class CancelSubscriptionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        try:
            subscription = Subscription.objects.get(user=user, is_active=True)

            # ❌ Cancel subscription in Stripe properly
            stripe.Subscription.modify(
                subscription.stripe_subscription_id,
                cancel_at_period_end=False,  # Use True if you want to cancel at the end of the billing cycle
            )

            # ✅ Mark subscription as inactive in database
            subscription.is_active = False
            subscription.save()

            return Response({"message": "Subscription canceled successfully."})

        except Subscription.DoesNotExist:
            return Response({"error": "No active subscription found."}, status=404)
        except stripe.error.StripeError as e:
            return Response({"error": f"Stripe error: {str(e)}"}, status=400)

class ListUserSubscriptionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        subscriptions = Subscription.objects.filter(user=user)
        
        data = []

        for sub in subscriptions:
            try:
                stripe_sub = stripe.Subscription.retrieve(sub.stripe_subscription_id)
                product_id = stripe_sub["items"]["data"][0]["price"]["product"]
                product = stripe.Product.retrieve(product_id)
                plan_name = product["name"]  # ✅ Get Plan Name Dynamically
            except stripe.error.StripeError as e:
                plan_name = "Unknown (Error fetching from Stripe)"

            # ✅ Append to response data
            data.append({
                "subscription_id": sub.stripe_subscription_id,
                "plan": plan_name,  # Use retrieved plan name
                "is_active": sub.is_active,
                "created_at": sub.created_at,
                "updated_at": sub.updated_at,
            })
        
        return Response({"subscriptions": data})

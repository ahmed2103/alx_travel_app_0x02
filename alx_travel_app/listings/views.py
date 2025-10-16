import uuid

from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Listing, Booking, Payment
from .serializers import ListingSerializer, BookingSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from ..settings import env
import requests
class ListingViewSet(viewsets.ModelViewSet):
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

@api_view(['POST'])
def process_payment(request):
    booking_id = request.data.get('booking_id')
    amount = request.data.get('amount')
    first_name = request.user.first_name
    last_name = request.user.last_name
    email = request.user.email
    if not all([booking_id, amount, first_name, last_name, email]):
        return Response({'error': 'Missing required fields'}, status=400)

    tx_ref = f"tx-{uuid.uuid4().hex[:10]}"
    chapa_url = "https://api.chapa.co/v1/transaction/initialize"
    headers = {
        "Authorization": f"Bearer {env('CHAPA_API_KEY')}",
        "Content-Type": "application/json"
    }
    data = {
                "amount": str(amount),
                "currency": "ETB",
                "email": email,
                "first_name": first_name,
                "last_name": last_name,
                "tx_ref": tx_ref,
                "customization[title]": "Booking Payment",
                "customization[description]": f"Payment for booking {booking_id}",
            }
    response = requests.post(chapa_url, headers=headers, json=data)
    response_data = response.json()
    if response.status_code != 200 or response_data.get('status') != 'success':
        return Response({'error': 'Payment initialization failed'}, status=500)
    checkout_data = response_data.get('data', {})
    payment = Payment.objects.create(
        booking =Booking.objects.get(id=booking_id),
        transaction_id = tx_ref,
        amount = amount,
        status = 'PENDING'
    )
    return Response({'checkout_url': checkout_data.get('checkout_url'), 'transaction_id': tx_ref})

@api_view(['GET'])
def verify_payment(request):
    tx_ref = request.query_params.get('tx_ref')
    if not tx_ref:
        return Response({'error': 'Missing transaction reference'}, status=400)

    chapa_url = f"https://api.chapa.co/v1/transaction/verify/{tx_ref}"
    headers = {
        "Authorization": f"Bearer {env('CHAPA_API_KEY')}",
        "Content-Type": "application/json"
    }
    response = requests.get(chapa_url, headers=headers)
    response_data = response.json()
    if response.status_code != 200 or response_data.get('status') != 'success':
        return Response({'error': 'Payment verification failed'}, status=500)

    payment_data = response_data.get('data', {})
    try:
        payment = Payment.objects.get(transaction_id=tx_ref)
        payment.status = 'COMPLETED' if payment_data.get('status') == 'successful' else 'FAILED'
        payment.save()
        return Response({'message': f'Payment {payment.status.lower()}'})
    except Payment.DoesNotExist:
        return Response({'error': 'Payment record not found'}, status=404)
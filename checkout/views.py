import stripe
import decimal
from rest_framework.views import APIView
from core.models import *
from rest_framework.response import Response
from .serializers import LinkSerializer
from rest_framework import exceptions
from django.db import transaction


class LinkAPIView(APIView):

    def get(self, _, code=''):
        link = Link.objects.filter(code=code).first()
        serializer = LinkSerializer(link)
        return Response(serializer.data)


class OrderAPIView(APIView):

    @transaction.atomic
    def post(self, request):
        data = request.data
        link = Link.objects.filter(code=data['code']).first()

        if not link:
            raise exceptions.APIException('Invalid code!')

        try:
            order = Order()
            order.code = link.code
            order.user_id = link.user.id
            order.ambassador_email = link.user.email
            order.first_name = data['first_name']
            order.last_name = data['last_name']
            order.email = data['email']
            order.address = data['address']
            order.country = data['country']
            order.city = data['city']
            order.zip = data['zip']
            order.save()

            line_items = []

            for item in data['products']:
                product = Product.objects.get(pk=item['product_id'])
                quantity = decimal.Decimal(item['quantity'])

                order_item = OrderItem()
                order_item.order = order
                order_item.product_title = product.title
                order_item.price = product.price
                order_item.quantity = quantity
                order_item.ambassador_revenue = decimal.Decimal(
                    .1) * product.price * quantity
                order_item.admin_revenue = decimal.Decimal(
                    .9) * product.price * quantity

                order_item.save()

                line_items.append({
                    'name': product.title,
                    'description': product.description,
                    'images': [
                        product.image
                    ],
                    'amount': int(100 * product.price),
                    'currency': 'usd',
                    'quantity': quantity
                })

            stripe.api_key = 'sk_test_51JC09hSJQxcdMnamZS9FVgsxq716rJo3dugne30RAlDFglvXr4qpW9Q40p41amj0kkgQqmpfdVCCxhQKM86DZCsk00diMVoXE8'

            source = stripe.checkout.Session.create(
                success_url='http://127.0.0.1:8000/success?source={CHECKOUT_SESSION_ID}',
                cancel_url='http://127.0.0.1:8000/error',
                payment_method_types=['card'],
                line_items=line_items,
                mode='payment',
            )

            order.transaction_id = source['id']
            order.save()

            return Response(source)

        except Exception as e:
            transaction.rollback()

            return Response({
                'message': 'Error occured!'
            })

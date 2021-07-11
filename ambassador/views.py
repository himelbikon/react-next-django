from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from core.models import Product
from .serializers import *
from rest_framework.permissions import IsAuthenticated
from common.authentication import JWTAuthentication
import time
import math
import random
import string


class ProductFrontendAPIView(APIView):
    @method_decorator(cache_page(60*60*2, key_prefix='products_frontend'))
    def get(self, _):
        time.sleep(2)
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)


class ProductBackendAPIView(APIView):

    def get(self, request):
        products = cache.get('products_backend')
        if not products:
            time.sleep(2)
            products = list(Product.objects.all())
            cache.set('products_backend', products, timeout=60*30)

        total = len(products)

        s = request.query_params.get('s', '')
        if s:
            set1 = set(Product.objects.filter(title__icontains=s))
            set2 = set(Product.objects.filter(description__icontains=s))
            products = list(set1.union(set2))
            total = len(products)

        sort = request.query_params.get('sort', None)
        if sort == 'asc':
            products.sort(key=lambda p: p.price)
        elif sort == 'desc':
            products.sort(key=lambda p: p.price, reverse=True)

        per_page = 9
        page = int(request.query_params.get('page', 1))
        start = (page - 1) * per_page
        end = page * per_page

        data = ProductSerializer(products[start:end], many=True).data

        return Response({
            'data': data,
            'meta': {
                'total': total,
                'page': page,
                'last_page': math.ceil(total / per_page)
            }
        })


class LinkAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        serializer = LinkSerializer(data={
            'user': user.id,
            'code': ''.join(random.choices(string.ascii_lowercase + string.digits, k=5)),
            'products': request.data['products']
        })
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)


class StatsAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        links = Link.objects.filter(user_id=user.id)

        return Response([self.format(link) for link in links])

    def format(self, link):
        orders = Order.objects.filter(code=link.code, complete=True)

        return {
            'code': link.code,
            'count': len(orders),
            'revenue': sum(o.ambassador_revenue for o in orders)
        }


class RankingsAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        ambassadors = User.objects.filter(is_ambassador=True)

        response = list(
            a.name + ': ' + str(a.revenue)
            for a in ambassadors)

        # response.sort(key=lambda a: a['name'], reverse=True)

        return Response(response)

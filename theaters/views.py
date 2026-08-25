from concurrent.futures import ThreadPoolExecutor

from django.conf import settings
from django.db import transaction
from rest_framework.decorators import action
from rest_framework.permissions import BasePermission, IsAuthenticated, IsAuthenticatedOrReadOnly, SAFE_METHODS
from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import ModelViewSet

from shops.models import TheaterShop
from shops.serializers import ShopSerializer
from .google_places import (
    preview_food_places, search_food_places, search_theater_candidates,
    search_theater_place,
)
from .models import Theater
from .serializers import TheaterSerializer


class IsTheaterOwnerOrStaff(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return bool(request.user.is_staff or obj.created_by_id == request.user.id)


class TheaterViewSet(ModelViewSet):
    queryset = Theater.objects.filter(is_active=True)
    serializer_class = TheaterSerializer
    lookup_field = 'slug'
    permission_classes = [IsAuthenticatedOrReadOnly, IsTheaterOwnerOrStaff]

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.query_params.get('q')
        if q:
            qs = qs.filter(name__icontains=q)
        return qs

    def perform_create(self, serializer):
        serializer.save(
            created_by=self.request.user,
            is_approved=self.request.user.is_staff,
        )

    @action(detail=False, methods=['get'])
    def candidates(self, request):
        query = request.query_params.get('q', '').strip()
        if len(query) < 2:
            return Response([])
        return Response(search_theater_candidates(query))

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def register(self, request):
        """Resolve a duplicate or create a user-editable pending theater."""
        name = request.data.get('name', '').strip()
        address = request.data.get('address', '').strip()
        place_id = request.data.get('google_place_id') or None
        if not name:
            return Response({'name': '劇場名は必須です。'}, status=status.HTTP_400_BAD_REQUEST)
        if not address and not place_id:
            return Response(
                {'address': '住所を入力するか、Googleの候補を選んでください。'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        existing = None
        if place_id:
            existing = Theater.objects.filter(google_place_id=place_id).first()
        if not existing:
            same_name = Theater.objects.filter(name__iexact=name)
            existing = same_name.filter(address__iexact=address).first() if address else same_name.first()
        if existing:
            data = dict(TheaterSerializer(existing, context={'request': request}).data)
            data['was_created'] = False
            return Response(data)

        payload = {
            'name': name,
            'address': address,
            'area_name': request.data.get('area_name', '').strip(),
            'prefecture': request.data.get('prefecture', '').strip(),
            'city': request.data.get('city', '').strip(),
            'google_place_id': place_id,
            'source_url': request.data.get('source_url', '').strip(),
        }
        serializer = self.get_serializer(data=payload)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            theater = serializer.save(
                created_by=request.user,
                is_approved=request.user.is_staff,
            )
        data = dict(self.get_serializer(theater).data)
        data['was_created'] = True
        return Response(data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'], url_path='google-places')
    def google_places(self, request):
        """Return short-lived Google photo data for the visible theater list."""
        queryset = self.filter_queryset(self.get_queryset())
        slugs = [slug for slug in request.query_params.get('slugs', '').split(',') if slug]
        if slugs:
            queryset = queryset.filter(slug__in=slugs)
        theaters = list(queryset[:12])
        if not theaters:
            return Response({})

        with ThreadPoolExecutor(max_workers=min(5, len(theaters))) as executor:
            places = executor.map(search_theater_place, theaters)
        return Response({
            theater.slug: (place or {})
            for theater, place in zip(theaters, places)
        })

    @action(detail=True, methods=['get'])
    def shops(self, request, slug=None):
        theater = self.get_object()
        theater_shops = TheaterShop.objects.filter(
            theater=theater, shop__is_active=True,
        ).select_related('shop').order_by('-is_featured', 'sort_order')
        theater_shops = list(theater_shops)
        shops = [ts.shop for ts in theater_shops]
        serializer = ShopSerializer(shops, many=True, context={'request': request})
        manual_results = [
            {
                **shop_data,
                'source': 'hoshidori',
                'listing_tier': (
                    'sponsored'
                    if theater_shop.is_featured or theater_shop.shop.is_featured
                    else 'recognized'
                ),
            }
            for theater_shop, shop_data in zip(theater_shops, serializer.data)
        ]

        if request.query_params.get('include_google') != '1':
            return Response(manual_results)

        manual_names = {shop.name.strip().casefold() for shop in shops}
        google_results = [
            place for place in search_food_places(theater)
            if place['name'].strip().casefold() not in manual_names
        ]
        if (
            not google_results
            and settings.DEBUG
            and request.query_params.get('preview_google') == '1'
        ):
            google_results = preview_food_places(theater)
        return Response([*manual_results, *google_results])

    @action(detail=True, methods=['get'], url_path='google-place')
    def google_place(self, request, slug=None):
        theater = self.get_object()
        return Response(search_theater_place(theater) or {})

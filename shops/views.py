from django.db.models import Case, Count, Exists, IntegerField, OuterRef, Q, Value, When
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from .models import Shop, ShopClickLog, ShopWantToGo, TheaterShop
from .serializers import ShopSerializer


class ShopViewSet(ReadOnlyModelViewSet):
    queryset = Shop.objects.filter(is_active=True)
    serializer_class = ShopSerializer
    lookup_field = 'slug'
    permission_classes = [AllowAny]

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.query_params.get('q', '').strip()
        category = self.request.query_params.get('category', '').strip()
        theater = self.request.query_params.get('theater', '').strip()

        if q:
            qs = qs.filter(Q(name__icontains=q) | Q(description__icontains=q))
        if category:
            qs = qs.filter(category__iexact=category)
        if theater:
            shop_ids = TheaterShop.objects.filter(
                theater__slug=theater,
            ).values_list('shop_id', flat=True)
            qs = qs.filter(id__in=shop_ids)

        # N+1回避: is_want_to_go をアノテーション
        user = self.request.user
        if user.is_authenticated:
            qs = qs.annotate(
                _is_want_to_go=Exists(
                    ShopWantToGo.objects.filter(user=user, shop_id=OuterRef('pk'))
                ),
            )

        featured_link = TheaterShop.objects.filter(
            shop_id=OuterRef('pk'),
            is_featured=True,
        )
        recognized_link = TheaterShop.objects.filter(
            shop_id=OuterRef('pk'),
            is_featured=False,
        )
        qs = qs.annotate(
            after_viewing_count=Count(
                'after_viewing_logs',
                filter=Q(after_viewing_logs__status='watched'),
                distinct=True,
            ),
            _has_featured_link=Exists(featured_link),
            _has_recognized_link=Exists(recognized_link),
        ).annotate(
            _listing_rank=Case(
                When(is_featured=True, then=Value(0)),
                When(_has_featured_link=True, then=Value(0)),
                When(_has_recognized_link=True, then=Value(1)),
                default=Value(2),
                output_field=IntegerField(),
            ),
        ).order_by('_listing_rank', 'featured_order', 'name')
        return qs

    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def featured(self, request):
        shops = Shop.objects.filter(
            is_active=True, is_featured=True,
        ).annotate(
            after_viewing_count=Count(
                'after_viewing_logs',
                filter=Q(after_viewing_logs__status='watched'),
                distinct=True,
            ),
        ).order_by('featured_order')[:6]
        serializer = self.get_serializer(shops, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def recognized(self, request):
        featured_link = TheaterShop.objects.filter(
            shop_id=OuterRef('pk'),
            is_featured=True,
        )
        shops = Shop.objects.filter(
            is_active=True,
            theater_shops__isnull=False,
        ).annotate(
            _has_featured_link=Exists(featured_link),
            _has_recognized_link=Exists(
                TheaterShop.objects.filter(shop_id=OuterRef('pk'), is_featured=False)
            ),
            after_viewing_count=Count(
                'after_viewing_logs',
                filter=Q(after_viewing_logs__status='watched'),
                distinct=True,
            ),
        ).filter(
            _has_featured_link=False,
        ).distinct().order_by('-after_viewing_count', 'name')[:8]
        serializer = self.get_serializer(shops, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[AllowAny])
    def click(self, request, slug=None):
        shop = self.get_object()
        ShopClickLog.objects.create(
            shop=shop,
            user=request.user if request.user.is_authenticated else None,
            source_type=request.data.get('source_type', ''),
            clicked_target=request.data.get('clicked_target', ''),
        )
        return Response({'detail': '記録しました。'}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post', 'delete'], url_path='want-to-go', permission_classes=[IsAuthenticated])
    def want_to_go(self, request, slug=None):
        shop = self.get_object()
        if request.method == 'POST':
            _, created = ShopWantToGo.objects.get_or_create(user=request.user, shop=shop)
            if created:
                return Response({'detail': '行きたい店に追加しました。'}, status=status.HTTP_201_CREATED)
            return Response({'detail': '既に登録済みです。'}, status=status.HTTP_200_OK)
        else:
            deleted, _ = ShopWantToGo.objects.filter(user=request.user, shop=shop).delete()
            if deleted:
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response({'detail': '登録されていません。'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'], url_path='want-to-go', permission_classes=[IsAuthenticated])
    def want_to_go_list(self, request):
        shop_ids = ShopWantToGo.objects.filter(
            user=request.user,
        ).order_by('-created_at').values_list('shop_id', flat=True)
        shops = Shop.objects.filter(id__in=shop_ids, is_active=True).annotate(
            after_viewing_count=Count(
                'after_viewing_logs',
                filter=Q(after_viewing_logs__status='watched'),
                distinct=True,
            ),
        )
        # 元の順序（新しい順）を維持
        shop_map = {s.id: s for s in shops}
        ordered = [shop_map[sid] for sid in shop_ids if sid in shop_map]
        serializer = self.get_serializer(ordered, many=True)
        return Response(serializer.data)

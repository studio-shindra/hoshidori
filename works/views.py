from rest_framework.decorators import action
from rest_framework.mixins import DestroyModelMixin
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from accounts.permissions import IsOwnerOrReadOnly
from .models import Performance, PerformanceCast, Person, PosterSubmission, Work
from .serializers import (
    PerformanceCastSerializer, PerformanceSerializer, PersonSerializer,
    PosterSubmissionSerializer, WorkSerializer,
)


class WorkViewSet(ModelViewSet):
    queryset = Work.objects.all()
    serializer_class = WorkSerializer
    lookup_field = 'slug'
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.query_params.get('q')
        if q:
            qs = qs.filter(title__icontains=q)
        person = self.request.query_params.get('person')
        if person:
            qs = qs.filter(performances__casts__person__name__icontains=person).distinct()
        return qs

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['get', 'post'], url_path='posters',
            parser_classes=[JSONParser, MultiPartParser, FormParser])
    def posters(self, request, slug=None):
        work = self.get_object()
        if request.method == 'GET':
            posters = PosterSubmission.objects.filter(work=work).select_related('user')
            serializer = PosterSubmissionSerializer(posters, many=True, context={'request': request})
            return Response(serializer.data)
        serializer = PosterSubmissionSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save(work=work, user=request.user, is_selected=True)
        return Response(serializer.data, status=201)

    @action(detail=False, methods=['get'], url_path='my-posters',
            permission_classes=[IsAuthenticated])
    def my_posters(self, request):
        posters = PosterSubmission.objects.filter(
            user=request.user,
        ).select_related('work', 'user').order_by('-created_at')
        serializer = PosterSubmissionSerializer(posters, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['delete'], url_path='my-posters/(?P<poster_id>[0-9]+)',
            permission_classes=[IsAuthenticated])
    def delete_my_poster(self, request, poster_id=None):
        try:
            poster = PosterSubmission.objects.get(id=poster_id, user=request.user)
        except PosterSubmission.DoesNotExist:
            return Response(status=404)
        poster.delete()
        return Response(status=204)


class PerformanceViewSet(ModelViewSet):
    queryset = Performance.objects.select_related('work', 'theater').prefetch_related('casts__person')
    serializer_class = PerformanceSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def get_queryset(self):
        qs = super().get_queryset()
        work = self.request.query_params.get('work')
        if work:
            qs = qs.filter(work_id=work)
        return qs

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'], url_path='add_cast',
            permission_classes=[IsAuthenticatedOrReadOnly])
    def add_cast(self, request, pk=None):
        performance = self.get_object()
        name = request.data.get('name', '').strip()
        role_name = request.data.get('role_name', '').strip()
        if not name:
            return Response({'name': '名前は必須です'}, status=400)
        person, _ = Person.objects.get_or_create(
            name=name,
            defaults={'created_by': request.user},
        )
        cast, created = PerformanceCast.objects.get_or_create(
            performance=performance,
            person=person,
            defaults={'role_name': role_name},
        )
        return Response(PerformanceCastSerializer(cast).data, status=201 if created else 200)


class PersonViewSet(ModelViewSet):
    queryset = Person.objects.all()
    serializer_class = PersonSerializer
    lookup_field = 'slug'
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.query_params.get('q')
        if q:
            qs = qs.filter(name__icontains=q)
        return qs

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class PerformanceCastViewSet(DestroyModelMixin, GenericViewSet):
    queryset = PerformanceCast.objects.all()
    serializer_class = PerformanceCastSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

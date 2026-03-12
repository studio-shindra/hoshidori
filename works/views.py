from rest_framework.decorators import action
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from accounts.permissions import IsOwnerOrReadOnly
from .models import Performance, Person, PosterSubmission, Work
from .serializers import (
    PerformanceSerializer, PersonSerializer, PosterSubmissionSerializer, WorkSerializer,
)


class WorkViewSet(ModelViewSet):
    queryset = Work.objects.all()
    serializer_class = WorkSerializer
    lookup_field = 'slug'
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.query_params.get('q')
        if q:
            qs = qs.filter(title__icontains=q)
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
        # POST
        serializer = PosterSubmissionSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save(work=work, user=request.user)
        return Response(serializer.data, status=201)


class PerformanceViewSet(ModelViewSet):
    queryset = Performance.objects.select_related('work', 'theater').prefetch_related('casts__person')
    serializer_class = PerformanceSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class PersonViewSet(ModelViewSet):
    queryset = Person.objects.all()
    serializer_class = PersonSerializer
    lookup_field = 'slug'
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

from django.db.models import Prefetch

from rest_framework.decorators import action
from rest_framework.mixins import DestroyModelMixin
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from accounts.permissions import IsOwnerOrReadOnly
from .models import Performance, PerformanceCast, Person, Work, WorkEditProposal
from .serializers import (
    PerformanceCastSerializer, PerformanceSerializer, PersonSerializer,
    WorkEditProposalSerializer, WorkSerializer,
)


class WorkViewSet(ModelViewSet):
    queryset = Work.objects.all()
    serializer_class = WorkSerializer
    lookup_field = 'slug'
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def get_queryset(self):
        qs = super().get_queryset().prefetch_related(
            Prefetch(
                'performances',
                queryset=Performance.objects.select_related('theater').order_by('-start_date'),
                to_attr='_prefetched_performances',
            ),
        )
        q = self.request.query_params.get('q')
        if q:
            qs = qs.filter(title__icontains=q)
        person = self.request.query_params.get('person')
        if person:
            qs = qs.filter(performances__casts__person__name__icontains=person).distinct()
        return qs

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'], url_path='propose-edit',
            permission_classes=[IsAuthenticated])
    def propose_edit(self, request, slug=None):
        work = self.get_object()
        submitted = {
            key: request.data[key]
            for key in ('title', 'description')
            if key in request.data
        }
        if not submitted:
            return Response({'detail': '変更内容を入力してください。'}, status=status.HTTP_400_BAD_REQUEST)
        validator = WorkSerializer(work, data=submitted, partial=True)
        validator.is_valid(raise_exception=True)
        changes = dict(validator.validated_data)
        proposal = WorkEditProposal.objects.create(
            work=work, proposed_by=request.user, changes=changes,
        )
        return Response(WorkEditProposalSerializer(proposal).data, status=status.HTTP_201_CREATED)

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

    @action(detail=True, methods=['post'], url_path='propose-edit',
            permission_classes=[IsAuthenticated])
    def propose_edit(self, request, pk=None):
        performance = self.get_object()
        submitted = {
            key: request.data[key]
            for key in ('theater', 'company_name', 'start_date', 'end_date', 'note')
            if key in request.data
        }
        if not submitted:
            return Response({'detail': '変更内容を入力してください。'}, status=status.HTTP_400_BAD_REQUEST)
        validator = PerformanceSerializer(performance, data=submitted, partial=True)
        validator.is_valid(raise_exception=True)
        changes = {}
        for key, value in validator.validated_data.items():
            if key == 'theater':
                changes[key] = value.pk
            elif hasattr(value, 'isoformat'):
                changes[key] = value.isoformat()
            else:
                changes[key] = value
        proposal = WorkEditProposal.objects.create(
            work=performance.work,
            performance=performance,
            proposed_by=request.user,
            changes=changes,
        )
        return Response(WorkEditProposalSerializer(proposal).data, status=status.HTTP_201_CREATED)

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

    @action(detail=False, methods=['get'], url_path='popular')
    def popular(self, request):
        from django.db.models import Count
        qs = Person.objects.annotate(
            work_count=Count('casts__performance__work', distinct=True),
        ).filter(work_count__gt=0).order_by('-work_count')[:20]
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)


class PerformanceCastViewSet(DestroyModelMixin, GenericViewSet):
    queryset = PerformanceCast.objects.all()
    serializer_class = PerformanceCastSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

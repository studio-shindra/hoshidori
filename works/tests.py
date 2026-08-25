from datetime import date
from io import StringIO

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import SimpleTestCase, TestCase, override_settings
from rest_framework.test import APIClient

from theaters.models import Theater
from .models import Performance, Work, WorkEditProposal


class SeedDemoSafetyTests(SimpleTestCase):
    @override_settings(DEBUG=False)
    def test_seed_demo_is_blocked_in_production(self):
        stderr = StringIO()

        call_command('seed_demo', stderr=stderr)

        self.assertIn('本番環境ではデモデータを投入できません', stderr.getvalue())


class WorkEditProposalTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.owner = user_model.objects.create_user(username='owner', password='password')
        self.editor = user_model.objects.create_user(username='editor', password='password')
        self.theater = Theater.objects.create(name='本田劇場', slug='honda', area_name='下北沢')
        self.work = Work.objects.create(title='元の作品', created_by=self.owner)
        self.performance = Performance.objects.create(
            work=self.work,
            theater=self.theater,
            start_date=date(2026, 8, 1),
            created_by=self.owner,
        )
        self.client = APIClient()

    def test_owner_can_edit_work_directly(self):
        self.client.force_authenticate(self.owner)
        response = self.client.patch(
            f'/api/works/{self.work.slug}/', {'title': '更新した作品'}, format='json',
        )
        self.assertEqual(response.status_code, 200)
        self.work.refresh_from_db()
        self.assertEqual(self.work.title, '更新した作品')

    def test_other_user_cannot_patch_but_can_propose_work_edit(self):
        self.client.force_authenticate(self.editor)
        denied = self.client.patch(
            f'/api/works/{self.work.slug}/', {'title': '勝手な更新'}, format='json',
        )
        self.assertEqual(denied.status_code, 403)

        proposed = self.client.post(
            f'/api/works/{self.work.slug}/propose-edit/',
            {'title': '修正案'}, format='json',
        )
        self.assertEqual(proposed.status_code, 201)
        proposal = WorkEditProposal.objects.get()
        self.assertEqual(proposal.status, 'pending')
        self.assertEqual(proposal.changes, {'title': '修正案'})

    def test_other_user_can_propose_performance_edit(self):
        self.client.force_authenticate(self.editor)
        proposed = self.client.post(
            f'/api/performances/{self.performance.id}/propose-edit/',
            {'company_name': '新しい団体'}, format='json',
        )
        self.assertEqual(proposed.status_code, 201)
        self.assertEqual(
            WorkEditProposal.objects.get().changes,
            {'company_name': '新しい団体'},
        )

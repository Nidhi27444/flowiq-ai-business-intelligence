import io
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from .models import Dataset
from .services import ImportValidationError, import_dataset, dataset_metrics, answer_question
CSV = b'order_date,customer,product,country,quantity,unit_price\n2025-02-01,Alice,Widget,Germany,2,10.50\n2026-03-01,Bob,Widget,France,1,9.00\n'
class DataTests(TestCase):
    def setUp(self):
        self.alice = User.objects.create_user('alice', password='TestPassword123!')
        self.bob = User.objects.create_user('bob', password='TestPassword123!')
        self.ds = import_dataset(self.alice, 'Demo', SimpleUploadedFile('sales.csv', CSV))

    def test_import_and_totals(self):
        metrics = dataset_metrics(self.ds)
        self.assertEqual(metrics['kpis']['revenue'], 30.0)
        self.assertEqual(metrics['kpis']['quantity'], 3)
        self.assertEqual(len(metrics['by_country']), 2)

    def test_invalid_csv_is_atomic(self):
        with self.assertRaises(ImportValidationError):
            import_dataset(self.alice, 'Bad', SimpleUploadedFile('x.csv', b'bad,columns\n1,2\n'))
        self.assertEqual(Dataset.objects.count(), 1)

    def test_questions(self):
        self.assertIn('Germany', answer_question('sales by country', dataset_metrics(self.ds)))

    def test_requires_login(self):
        self.assertEqual(self.client.get(reverse('dashboard')).status_code, 302)
        self.assertEqual(self.client.get(reverse('api_metrics', args=[self.ds.id])).status_code, 302)

    def test_cross_user_isolation(self):
        self.client.force_login(self.bob)
        self.assertEqual(self.client.get(reverse('api_metrics', args=[self.ds.id])).status_code, 404)
        self.assertEqual(self.client.post(reverse('api_ask', args=[self.ds.id]), data='{}', content_type='application/json').status_code,404)
        self.assertEqual(self.client.get(reverse('export_report', args=[self.ds.id])).status_code,404)

    def test_owner_api(self):
        self.client.force_login(self.alice)
        resp = self.client.get(reverse('api_metrics', args=[self.ds.id]))
        self.assertEqual(resp.json()['kpis']['revenue'], 30.0)
        answer = self.client.post(reverse('api_ask', args=[self.ds.id]), data='{"question":"revenue"}', content_type='application/json')
        self.assertEqual(answer.status_code,200)
        self.assertIn('30.00',answer.json()['answer'])

    def test_delete_requires_post(self):
        self.client.force_login(self.alice)
        self.assertEqual(self.client.get(reverse('delete_dataset', args=[self.ds.id])).status_code,405)
        self.assertEqual(Dataset.objects.count(),1)

    def test_monthly_series_and_insights(self):
        from .services import automatic_insights
        metrics = dataset_metrics(self.ds)
        self.assertEqual([r['month'] for r in metrics['by_month']], ['2025-02','2026-03'])
        self.assertTrue(any('Top country' in x for x in automatic_insights(metrics)))

    def test_conversational_dataset_filters(self):
        from .services import conversational_answer
        self.assertIn('€21.00', conversational_answer('Revenue for Germany in 2025', self.ds))
        self.assertIn('No matching', conversational_answer('Revenue in Germany in 2024', self.ds))

    def test_insights_api_requires_ownership(self):
        self.client.force_login(self.bob)
        self.assertEqual(self.client.get(reverse('api_insights',args=[self.ds.pk])).status_code,404)
        self.assertEqual(self.client.post(reverse('api_ai_ask',args=[self.ds.pk]),data='{}',content_type='application/json').status_code,404)
        self.client.force_login(self.alice)
        self.assertEqual(self.client.get(reverse('api_insights',args=[self.ds.pk])).status_code,200)
        self.assertEqual(self.client.post(reverse('api_ai_ask',args=[self.ds.pk]),data='{"question":"revenue"}',content_type='application/json').status_code,400)

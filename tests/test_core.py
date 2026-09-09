import os
import tempfile
import unittest
from datetime import datetime
from unittest.mock import patch, Mock
from zoneinfo import ZoneInfo

from analysis import growth, valuation, score
from calendar_sync import event_body, upsert
from providers import demo
from storage import Store
from weekly_review import run


class CoreTests(unittest.TestCase):
    def test_valuation_units_and_invalid_inputs(self):
        a = dict(profit=100, multiple=10, debt=200, shares=10)
        self.assertEqual(valuation(8000, a)['Base'], 8000)
        self.assertEqual(valuation(8000, a)['gap'], 0)
        self.assertIsNone(valuation(8000, {**a, 'shares': 0}))
        self.assertIsNone(growth(100, -10))

    def test_missing_evidence_does_not_make_total(self):
        self.assertIsNone(score(demo())['total'])
        self.assertIsNone(score(demo())['scores']['엣지'])

    def test_stable_calendar_id(self):
        zone = ZoneInfo('Asia/Seoul')
        a = event_body('005930', datetime(2026, 9, 7, 8, tzinfo=zone))
        b = event_body('005930', datetime(2026, 9, 9, 10, tzinfo=zone))
        self.assertEqual(a['id'], b['id'])
        self.assertNotEqual(a['id'], event_body('000660', datetime(2026, 9, 7, tzinfo=zone))['id'])
        self.assertNotIn('attendees', a)

    def test_existing_calendar_event_is_updated(self):
        from googleapiclient.errors import HttpError
        import httplib2
        service = Mock()
        service.events().insert().execute.side_effect = HttpError(httplib2.Response({'status':409}), b'{}')
        body = event_body('005930')
        upsert(service, 'calendar', body)
        self.assertEqual(service.events().patch.call_args.kwargs['eventId'], body['id'])

    def test_dry_run_failure_and_live_persistence(self):
        with tempfile.TemporaryDirectory() as folder, patch.dict(os.environ, {'SUPABASE_URL':'', 'SUPABASE_SERVICE_ROLE_KEY':''}):
            store = Store(folder+'/state.json')
            store.save_stock({'code':'005930','year':2025,'review_enabled':True})
            original = store.read()
            provider = Mock()
            provider.report.return_value = {**demo(), 'sample':False}
            with patch('weekly_review.upsert') as calendar:
                self.assertEqual(run(store, provider)['processed'], 1)
                calendar.assert_not_called()
                self.assertEqual(store.read(), original)
                provider.report.side_effect = RuntimeError('provider failure')
                self.assertEqual(run(store, provider, dry=False)['failed'], 1)
                self.assertEqual(store.read()['stocks'], original['stocks'])
                provider.report.side_effect = None
                self.assertEqual(run(store, provider, dry=False)['processed'], 1)
                self.assertEqual(len(store.read()['journal']), 1)
                self.assertIn('last_success', store.read()['stocks'][0])


if __name__ == '__main__':
    unittest.main()

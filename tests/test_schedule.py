import mock
import unittest
from click import ClickException
from click.testing import CliRunner
from shub import schedule


class ScheduleTest(unittest.TestCase):

    def setUp(self):
        self.runner = CliRunner()

    @mock.patch('shub.schedule.find_api_key', autospec=True)
    def test_apikey_is_validated(self, mock_find_apikey):
        mock_find_apikey.return_value = None
        output = self.runner.invoke(schedule.cli, ['fake_spider', '-p', 1]).output
        err = 'Unexpected output: %s' % output
        self.assertTrue('key not found' in output, err)

    @mock.patch('shub.schedule.find_api_key', autospec=True)
    @mock.patch('shub.schedule.schedule_spider', autospec=True)
    def test_schedules_job_if_input_is_ok(self, mock_find_apikey, mock_schedule_spider):
        mock_find_apikey.return_value = 1
        self.runner.invoke(schedule.cli, ['fake_spider', '-p', 1])
        self.assertTrue(mock_schedule_spider.called)

    @mock.patch('shub.schedule.Connection', spec=True)
    def test_schedule_spider_raises_click_exception_with_invalid_spider(self, mock_conn):
        mock_conn.return_value.project_ids.return_value = [1]
        mock_conn.return_value.__getitem__.return_value.id = 1
        mock_conn.return_value.__getitem__.return_value.spiders.return_value = []
        self.assertRaisesRegexp(
            ClickException, "spider fake_spider doesn\'t exist in project 1",
            schedule.schedule_spider, 'FAKE_API_KEY', 1, 'fake_spider'
        )

    @mock.patch('shub.schedule.Connection', spec=True)
    def test_schedule_spider_calls_project_schedule(self, mock_conn):
        mock_conn = mock_conn.return_value
        mock_conn.project_ids.return_value = [1]
        mock_conn.__getitem__.return_value.spiders.return_value = [{'id': 'fake_spider'}]
        mock_conn.__getitem__.return_value.id = 1
        mock_conn.__getitem__.return_value.schedule.return_value = mock.sentinel.jobkey
        jobkey = schedule.schedule_spider('FAKE_API_KEY', 1, 'fake_spider')
        self.assertEqual(jobkey, mock.sentinel.jobkey)


if __name__ == '__main__':
    unittest.main()

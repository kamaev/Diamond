#!/usr/bin/python
# coding=utf-8
##########################################################################

from test import CollectorTestCase
from test import get_collector_config
from test import unittest
from mock import Mock
from mock import call
from mock import patch

from diamond.collector import Collector
from smart import SmartCollector

##########################################################################


class TestSmartCollector(CollectorTestCase):

    def setUp(self):
        config = get_collector_config('SmartCollector', {
            'interval': 10,
            'bin': 'true',
            'path': 'test',
            'devices': ['sda', 'disk0'],
            'valtypes': ['raw_val'],
            'attributes': {
                'spin_up_time': True,
                'power_cycle_count': True,
                'temperature_celsius': True,
                '172': True},
            'aliases': {
                'disk0': {
                    '172': 'some_attribute'}},
            'force_prefails': True
        })

        self.collector = SmartCollector(config, None)

    def test_import(self):
        self.assertTrue(SmartCollector)

    @patch('os.access', Mock(return_value=True))
    @patch.object(Collector, 'publish')
    def test_should_work_with_real_data_osx_missing(self, publish_mock):
        patch_listdir = patch('os.listdir', Mock(return_value=['disk0']))
        patch_communicate = patch(
            'subprocess.Popen.communicate',
            Mock(return_value=(
                self.getFixture('osx_missing').getvalue(),
                '')))
        patch_listdir.start()
        patch_communicate.start()
        self.collector.collect()
        patch_listdir.stop()
        patch_communicate.stop()

        self.assertPublishedMany(publish_mock, {})

    @patch('os.access', Mock(return_value=True))
    @patch.object(Collector, 'publish')
    def test_should_work_with_real_data_osx_ssd(self, publish_mock):
        patch_listdir = patch('os.listdir', Mock(return_value=['disk0']))
        patch_communicate = patch(
            'subprocess.Popen.communicate',
            Mock(return_value=(
                self.getFixture('osx_ssd').getvalue(),
                '')))
        patch_listdir.start()
        patch_communicate.start()
        self.collector.collect()
        patch_listdir.stop()
        patch_communicate.stop()

        self.assertPublishedMany(publish_mock, {
            'disk0.old_age.raw_val.some_attribute': 0
        })

    @patch('os.access', Mock(return_value=True))
    @patch.object(Collector, 'publish')
    def test_should_work_with_real_data_centos55_hdd(self, publish_mock):
        patch_listdir = patch('os.listdir', Mock(return_value=['sda']))
        patch_communicate = patch(
            'subprocess.Popen.communicate',
            Mock(return_value=(
                self.getFixture('centos5.5_hdd').getvalue(),
                '')))

        patch_listdir.start()
        patch_communicate.start()
        self.collector.collect()
        patch_listdir.stop()
        patch_communicate.stop()

        metrics = {
            'sda.pre-fail.raw_val.spin_up_time': 3991
        }

        self.setDocExample(collector=self.collector.__class__.__name__,
                           metrics=metrics,
                           defaultpath=self.collector.config['path'])
        self.assertPublishedMany(publish_mock, metrics)

    @patch('os.access', Mock(return_value=True))
    @patch.object(Collector, 'publish')
    def test_should_work_with_real_data_debian_invalid_checksum_warning(
            self, publish_mock):
        fixture_data = self.getFixture(
            'debian_invalid_checksum_warning').getvalue()
        patch_listdir = patch('os.listdir', Mock(return_value=['sda']))
        patch_communicate = patch('subprocess.Popen.communicate',
                                  Mock(return_value=(fixture_data, '')))

        patch_listdir.start()
        patch_communicate.start()
        self.collector.collect()
        patch_listdir.stop()
        patch_communicate.stop()

        metrics = {
            'sda.old_age.raw_val.temperature_celsius': 35
        }

        header_call = call('sda.ATTRIBUTE_NAME', 'RAW_VALUE')
        published_metric_header = header_call in publish_mock.mock_calls
        assert not published_metric_header, "published metric for header row"

        self.assertPublishedMany(publish_mock, metrics)

    def test_find_attr_start_line(self):
        def get_fixture_lines(fixture):
            return self.getFixture(fixture).getvalue().strip().splitlines()

        def assert_attrs_start_at(expected, fixture):
            lines = get_fixture_lines(fixture)
            self.assertEqual(expected,
                             self.collector.find_attr_start_line(lines))

        lines = get_fixture_lines('osx_missing')
        self.assertEqual(5, self.collector.find_attr_start_line(lines, 2, 4))

        assert_attrs_start_at(7, 'osx_ssd')
        assert_attrs_start_at(7, 'centos5.5_hdd')
        assert_attrs_start_at(8, 'debian_invalid_checksum_warning')

##########################################################################
if __name__ == "__main__":
    unittest.main()

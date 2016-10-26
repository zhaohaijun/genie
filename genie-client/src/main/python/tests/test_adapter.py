from __future__ import absolute_import, division, print_function, unicode_literals

import unittest

from mock import call, patch
from nose.tools import (assert_equals,
                        assert_raises)

from pygenie.adapter.genie_x import substitute
from pygenie.adapter.genie_3 import (Genie3Adapter,
                                     get_payload)
from pygenie.jobs import PrestoJob
from pygenie.exceptions import GenieLogNotFoundError

from .utils import fake_response


@patch.dict('os.environ', {'GENIE_BYPASS_HOME_CONFIG': '1'})
class TestStringSubstitution(unittest.TestCase):
    """Test script parameter substitution."""

    def test_substitute(self):
        """Test script parameter substitution."""

        assert_equals(
            substitute('hello $name, goodbye $last',
                       dict(name='test1', last='bye1')),
            'hello test1, goodbye bye1'
        )

    def test_substitute_expansion(self):
        """Test script parameter substitution (expansion)."""

        assert_equals(
            substitute('hello ${name}, goodbye ${last}',
                       dict(name='test2', last='bye2')),
            'hello test2, goodbye bye2'
        )

    def test_substitute_missing(self):
        """Test script parameter substitution with missing parameters."""

        assert_equals(
            substitute('hello $name, goodbye $last',
                       dict(name='tester3')),
            'hello tester3, goodbye $last'
        )

    def test_substitute_missing_expansion(self):
        """Test script parameter substitution with missing parameters (expansion)."""

        assert_equals(
            substitute('hello ${name}, goodbye ${last}',
                       dict(name='tester4')),
            'hello tester4, goodbye ${last}'
        )


@patch.dict('os.environ', {'GENIE_BYPASS_HOME_CONFIG': '1'})
class TestGenie3Adapter(unittest.TestCase):
    """Test Genie 3 adapter."""

    @patch('pygenie.utils.requests.request')
    def test_stderr_log_not_found(self, request):
        """Test Genie 3 adapter getting stderr log which does not exist."""

        request.return_value = fake_response(None, status_code=404)

        adapter = Genie3Adapter()

        with assert_raises(GenieLogNotFoundError):
            adapter.get_stderr('job_id_dne')

    def test_set_job_name_with_script_has_params(self):
        """Test Genie 3 adapter setting job name (if not set) with script containing parameters."""

        job = PrestoJob() \
            .script('select * from ${table}') \
            .parameter('table', 'foo.fizz')

        payload = get_payload(job)

        assert_equals(
            'select * from {table}',
            payload['name']
        )

    @patch('pygenie.adapter.genie_3.Genie3Adapter.get')
    def test_get_info_for_rj_all(self, get):
        """Test Genie 3 adapter get info call for job (all)."""

        adapter = Genie3Adapter()
        adapter.get_info_for_rj('111-all')

        assert_equals(
            [
                call('111-all', timeout=30),
                call('111-all', path='request', timeout=30),
                call('111-all', if_not_found=[], path='applications', timeout=30),
                call('111-all', if_not_found={}, path='cluster', timeout=30),
                call('111-all', if_not_found={}, path='command', timeout=30),
                call('111-all', if_not_found={}, path='execution', timeout=30)
            ],
            get.call_args_list
        )

    @patch('pygenie.adapter.genie_3.Genie3Adapter.get')
    def test_get_info_for_rj_all_timeout(self, get):
        """Test Genie 3 adapter get info call for job (all) (with timeout)."""

        adapter = Genie3Adapter()
        adapter.get_info_for_rj('111-all-timeout', timeout=1)

        assert_equals(
            [
                call('111-all-timeout', timeout=1),
                call('111-all-timeout', path='request', timeout=1),
                call('111-all-timeout', if_not_found=[], path='applications', timeout=1),
                call('111-all-timeout', if_not_found={}, path='cluster', timeout=1),
                call('111-all-timeout', if_not_found={}, path='command', timeout=1),
                call('111-all-timeout', if_not_found={}, path='execution', timeout=1)
            ],
            get.call_args_list
        )

    @patch('pygenie.adapter.genie_3.Genie3Adapter.get')
    def test_get_info_for_rj_job(self, get):
        """Test Genie 3 adapter get info call for job (job section)."""

        adapter = Genie3Adapter()
        adapter.get_info_for_rj('111-job', job=True)

        assert_equals(
            [
                call('111-job', timeout=30)
            ],
            get.call_args_list
        )
# -*- coding: utf-8 -*-
#
# Copyright 2012-2015 Spotify AB
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import luigi
import tempfile
import shlex
from helpers import unittest
from luigi.contrib.hadoop_jar import HadoopJarJobError, HadoopJarJobTask
from mock import patch, MagicMock


class TestHadoopJarJob(HadoopJarJobTask):
    path = luigi.Parameter()

    def jar(self):
        return self.path


class TestMissingJarJob(HadoopJarJobTask):
    pass


class TestRemoteHadoopJarJob(TestHadoopJarJob):
    def ssh(self):
        return {"host": "myhost", "key_file": "file", "username": "user"}


class TestRemoteMissingJarJob(TestHadoopJarJob):
    def ssh(self):
        return {"host": "myhost", "key_file": "file"}


class TestRemoteHadoopJarTwoParamJob(TestRemoteHadoopJarJob):
    param2 = luigi.Parameter()


class HadoopJarJobTaskTest(unittest.TestCase):
    @patch('luigi.contrib.hadoop.run_and_track_hadoop_job')
    def test_good(self, mock_job):
        mock_job.return_value = None
        with tempfile.NamedTemporaryFile() as temp_file:
            task = TestHadoopJarJob(temp_file.name)
            task.run()

    @patch('luigi.contrib.hadoop.run_and_track_hadoop_job')
    def test_missing_jar(self, mock_job):
        mock_job.return_value = None
        task = TestMissingJarJob()
        self.assertRaises(HadoopJarJobError, task.run)

    @patch('luigi.contrib.hadoop.run_and_track_hadoop_job')
    def test_remote_job(self, mock_job):
        mock_job.return_value = None
        with tempfile.NamedTemporaryFile() as temp_file:
            task = TestRemoteHadoopJarJob(temp_file.name)
            task.run()

    @patch('luigi.contrib.hadoop.run_and_track_hadoop_job')
    def test_remote_job_with_space_in_task_id(self, mock_job):
        with tempfile.NamedTemporaryFile() as temp_file:

            def check_space(arr, task_id):
                for a in arr:
                    if a.startswith('hadoop jar'):
                        found = False
                        for x in shlex.split(a):
                            if task_id in x:
                                found = True
                        if not found:
                            raise AssertionError

            task = TestRemoteHadoopJarTwoParamJob(temp_file.name, 'test')
            mock_job.side_effect = lambda x: check_space(x, task.task_id)
            task.run()

    @patch('luigi.contrib.hadoop.run_and_track_hadoop_job')
    def test_remote_job_missing_config(self, mock_job):
        mock_job.return_value = None
        with tempfile.NamedTemporaryFile() as temp_file:
            task = TestRemoteMissingJarJob(temp_file.name)
            self.assertRaises(HadoopJarJobError, task.run)

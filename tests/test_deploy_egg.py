#!/usr/bin/env python
# coding=utf-8

from __future__ import print_function

import unittest
import os
import tempfile
import shutil

from shub import deploy_egg


class FakeRequester:
    """Used to mock shub.utils#make_deploy_request"""
    def fake_request(self, *args):
        self.url = args[0]
        self.data = args[1]
        self.files = args[2]
        self.auth = args[3]


class TestDeployEgg(unittest.TestCase):


    def setUp(self):
        self.curdir = os.getcwd()

        self.fake_requester = FakeRequester()
        deploy_egg.make_deploy_request = self.fake_requester.fake_request

        self.tmp_dir = tempfile.mkdtemp(prefix="shub-test-deploy-eggs")
        shutil.rmtree(self.tmp_dir)


    def tearDown(self):
        os.chdir(self.curdir)


    def test_parses_project_information_correctly(self):
        # this test's assertions are based on the values
        # defined on this folder's setup.py file
        shutil.copytree('tests/samples/deploy_egg_sample_project/', self.tmp_dir)
        os.chdir(self.tmp_dir)

        data = self.call_main_and_check_request_data()
        self.assertEqual('test_project-1.2.0', data['version'])


    def test_can_clone_a_git_repo_and_deploy_the_egg(self):
        repo = os.path.abspath('tests/samples/deploy_egg_sample_repo.git')
        self.call_main_and_check_request_data(from_url=repo)
        data = self.call_main_and_check_request_data()
        self.assertTrue('master' in data['version'])


    def test_can_clone_checkout_and_deploy_the_egg(self):
        repo = os.path.abspath('tests/samples/deploy_egg_sample_repo.git')
        branch = 'dev'
        data = self.call_main_and_check_request_data(from_url=repo, git_branch=branch)
        self.assertTrue('dev' in data['version'])


    def call_main_and_check_request_data(self, project_id=0, from_url=None,
                                         git_branch=None):
        # WHEN
        deploy_egg.main(project_id, from_url, git_branch)

        data = self.fake_requester.data
        files = self.fake_requester.files

        # THEN
        # the egg was successfully built, let's check the data
        # that is sent to the scrapy cloud
        self.assertTrue('test_project', files['egg'][0])
        self.assertEqual(project_id, data['project'])
        self.assertEqual('test_project', data['name'])

        return data


if __name__ == '__main__':
    unittest.main()

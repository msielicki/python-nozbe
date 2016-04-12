#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Mariusz Sielicki <mariusz.sielicki@gmail.com>
import logging
import requests

log = logging.getLogger("nozbe")


class Nozbe(object):
    API_URL = 'https://webapp.nozbe.com/api'
    API_KEY = None
    SESSION = None
    ACTIONS = ('projects', 'contexts', 'newproject', 'actions', 'newaction')

    def __init__(self, api_key, username=None, password=None):
        if api_key is not None:
            self.API_KEY = api_key
        if self.SESSION is None:
            self.SESSION = requests.Session()

    def _prepare_url(self, action, *args, **kwargs):
        if action not in self.ACTIONS:
            log.error('Unsupported action: %s', action)
            raise AttributeError

        url = [self.API_URL, action]

        if args:
            url.append(*args)

        if kwargs:
            url.append('/'.join(['{}-{}'.format(k, v) for k, v in kwargs.items()]))

        url.append('key-{}'.format(self.API_KEY))
        return '/'.join(url)

    def _fetch(self, url):
        log.info('Request for url: %s', url)
        res = self.SESSION.get(url)
        try:
            ret = res.json()
        except ValueError:
            log.debug('Request for url: %s', url)
            ret = []
        return ret

    def get_projects(self):
        url = self._prepare_url('projects')
        return self._fetch(url)

    def get_project_by_name(self, name):
        for project in self.get_projects():
            if name == project['name']:
                return project

    def get_project_by_id(self, project_id):
        for project in self.get_projects():
            if project_id == project['id']:
                return project

    def get_project_tasks(self, id=None, name=None):
        if id is not None:
            project_id = id
        elif name is not None:
            project = self.get_project_by_name(name)
            project_id = project['id']
        else:
            log.error('Project id or name must be provided')
            raise AttributeError

        url = self._prepare_url('actions', what='project', id=project_id)
        return self._fetch(url)

    def get_contexts(self):
        url = self._prepare_url('contexts')
        return self._fetch(url)

    def create_project(self, name, force=False):
        if not force:
            projects = self.get_projects()
            if name in [i['name'] for i in projects]:
                log.warn('Project with name "%s" already exists.', name)
                return projects
        url = self._prepare_url('newproject', name=name)
        self._fetch(url)
        return self.get_projects()

    def create_project_task(self, name, project_id):
        url = self._prepare_url('newaction', name=name, project_id=project_id)
        self._fetch(url)
        return self.get_project_tasks(project_id)

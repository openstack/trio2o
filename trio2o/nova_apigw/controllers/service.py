#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from pecan import expose
from pecan import rest

import trio2o.common.client as t_client
import trio2o.common.context as t_context

SUPPORTED_FILTERS = {
    'host': 'host',
    'binary': 'binary',
}


class ServiceController(rest.RestController):

    def __init__(self, project_id):
        self.project_id = project_id
        self.client = t_client.Client()

    def _construct_compute_entry(self, compute):
        if not isinstance(compute, dict):
            compute = compute.to_dict()
        return {
            'id': compute['id'],
            'binary': compute['binary'],
            'host': compute['host'],
            'state': compute.get('state'),
            'zone': compute.get('zone'),
            'status': compute.get('status'),
            'updated_at': compute.get('updated_at'),
        }

    @expose(generic=True, template='json')
    def get_all(self, **kwargs):
        context = t_context.extract_context_from_environ()
        filters = self._get_filters(kwargs)
        filters = [{'key': key,
                    'comparator': 'eq',
                    'value': value} for key, value in filters.iteritems()]
        services = getattr(self.client, 'services').list(context,
                                                         filters=filters)
        ret_services = [self._construct_compute_entry(
            service) for service in services]
        return {'services': ret_services}

    def _get_filters(self, params):
        """Return a dictionary of query param filters from the request.

        :param params: the URI params coming from the wsgi layer
        :return a dict of key/value filters
        """
        filters = {}
        for param in params:
            if param in SUPPORTED_FILTERS:
                filter_name = SUPPORTED_FILTERS.get(param, param)
                filters[filter_name] = params.get(param)

        return filters

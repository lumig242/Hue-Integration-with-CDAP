#!/usr/bin/env python
# Licensed to Cloudera, Inc. under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  Cloudera, Inc. licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from desktop.lib.django_util import render
from django.http import HttpResponse
from cdap.client import auth_client
from cdap.conf import CDAP_API_HOST, CDAP_API_PORT, CDAP_API_VERSION
from libsentry.api2 import get_api

import urllib2
import json
import logging

LOG = logging.getLogger(__name__)
# BASE_URL = "http://{}:{}/{}".format(CDAP_API_HOST.get(), CDAP_API_PORT.get(), CDAP_API_VERSION.get())
BASE_URL = "http://rohit9692-1000.dev.continuuity.net:10000/v3"
CDAP_CLIENT = auth_client(BASE_URL)
ENTITIES_ALL = dict()


def _call_cdap_api(url):
  return CDAP_CLIENT.get(url)


def index(request):
  global ENTITIES_ALL
  namespace_url = "/namespaces"
  namespaces = _call_cdap_api(namespace_url)
  # entities = {ns.get("name"): dict() for ns in namespaces}
  entities = dict((ns.get("name"), dict()) for ns in namespaces)
  ENTITIES_ALL = dict((ns.get("name"), ns) for ns in namespaces)

  apis = {
    "stream": "/streams",
    "dataset": "/data/datasets",
    "artifact": "/artifacts",
    "application": "/apps",
  }

  for ns in entities:
    for entity_type, entity_url in apis.items():
      full_url = namespace_url + "/" + ns + entity_url
      items = _call_cdap_api(full_url)

      if entity_type == "application":
        entities[ns][entity_type] = {}
        ENTITIES_ALL[ns][entity_type] = {}
        # Application has addtional hierarchy
        for item in items:
          programs = _call_cdap_api(full_url + "/" + item["name"])["programs"]
          program_dict = dict()
          for program in programs:
            if program["type"] not in program_dict:
              program_dict[program["type"].lower()] = list()
            program_dict[program["type"].lower()].append(program)
          entities[ns][entity_type][item["name"]] = program_dict
          ENTITIES_ALL[ns][entity_type][item["name"]] = dict((p_type, dict((p["name"], p)))
                                                         for p_type, programs in program_dict.items()
                                                         for p in programs)
          ENTITIES_ALL[ns][entity_type][item["name"]].update(item)
      else:
        entities[ns][entity_type] = [item.get("name") for item in items]
        ENTITIES_ALL[ns][entity_type] = dict((item.get("name"), item) for item in items)

  print entities
  print ENTITIES_ALL
  return render('index.mako', request, dict(date2="testjson", entities=entities))


def details(request, path):
  item = ENTITIES_ALL
  for k in path.strip("/").split("/"):
    item = item[k]
  return HttpResponse(json.dumps(item).replace("\n", ""), content_type="application/json")


def list_privileges(request, path):
  try:
    # TODO: Use this path to retrieve all the privileges
    path.strip("/").split("/")
  except Exception as e:
    LOG.exception("could not retrieve roles")
  return


def grant_privilege(request):
  return


def revoke_privilege(request):
  return


def list_roles_by_group(request):
  sentry_privileges = get_api(request.user, "cdap").list_sentry_roles_by_group()
  #sentry_privileges = [{"name": "testrole2", "groups": []}, {"name": "testrole1", "groups": []}]
  print sentry_privileges
  return HttpResponse(json.dumps(sentry_privileges), content_type="application/json")


def list_privileges_by_authorizable(request):
  sentry_privileges = get_api(request.user, "cdap").list_sentry_privileges_by_role("cdap", "testRole1")
  print sentry_privileges
  return HttpResponse(json.dumps(sentry_privileges), content_type="application/json")
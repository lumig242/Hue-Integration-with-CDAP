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
from django.http import HttpResponse, HttpResponseRedirect, HttpResponse
from cdap.client import auth_client
from cdap.conf import CDAP_API_HOST, CDAP_API_PORT, CDAP_API_VERSION
from libsentry.api2 import get_api

import urllib2
import json
import logging

from collections import defaultdict

LOG = logging.getLogger(__name__)
# BASE_URL = "http://{}:{}/{}".format(CDAP_API_HOST.get(), CDAP_API_PORT.get(), CDAP_API_VERSION.get())
BASE_URL = "http://rohit9692-1000.dev.continuuity.net:10000/v3"
CDAP_CLIENT = auth_client(BASE_URL)
ENTITIES_ALL = dict()


def _call_cdap_api(url):
  return CDAP_CLIENT.get(url)

def cdap_authenticate(request):
  print request.POST["username"]
  print request.POST["password"]
  CDAP_CLIENT.set_credentials(request.POST["username"], request.POST["password"])
  return HttpResponse()

def index(request):
  global ENTITIES_ALL
  if not CDAP_CLIENT.is_set_credentials:
    return render('index.mako', request, dict(date2="testjson", unauthenticated=True))
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
    for entity_type, entity_url in apis.iteritems():
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
          ENTITIES_ALL[ns][entity_type][item["name"]] = dict((p_type, {p["name"]:p})
                                                             for p_type, programs in program_dict.iteritems()
                                                             for p in programs)
          ENTITIES_ALL[ns][entity_type][item["name"]].update(item)
      else:
        entities[ns][entity_type] = [item.get("name") for item in items]
        ENTITIES_ALL[ns][entity_type] = dict((item.get("name"), item) for item in items)

  return render('index.mako', request, dict(date2="testjson", entities=entities))


def _match_authorizables(authorizables, path):
  i = 0
  for auth in authorizables:
    if i >= len(path):
      return False
    if auth["type"].lower() != path[i].lower() or \
      auth["name"].lower() != path[i+1].lower():
      return False
    i += 2
  return True

def details(request, path):
  item = ENTITIES_ALL
  for k in path.strip("/").split("/"):
    item = item[k]

  api = get_api(request.user, "cdap")
  # Fetch all the privileges from sentry first
  roles = [result["name"] for result in api.list_sentry_roles_by_group()]
  privileges = []

  # Construct the full path for security
  path = path.strip("/").split("/")
  path = ["instance","cdap","namespace"] + path

  for role in roles:
    sentry_privilege = api.list_sentry_privileges_by_role("cdap", role)
    for privilege in sentry_privilege:
      for auth in privilege["authorizables"]:
        if _match_authorizables(auth, path):
          privileges.append({"role":role, "actions":privilege["action"]})

  item["privileges"] = privileges
  return HttpResponse(json.dumps(item), content_type="application/json")


def _to_sentry_privilege(action):
  return {
    "component": "cdap",
    "serviceName": "cdap",
    "authorizables": [{"type": "INSTANCE", "name": "cdap"}, {"type": "NAMESPACE", "name": "demospace"}, {"type": "STREAM", "name": "purchasestream"}],
    "action": action,
  }


def grant_privileges(request):
  tSentryPrivilege = _to_sentry_privilege("ALL")
  result = get_api(request.user, "cdap").alter_sentry_role_grant_privilege("testrole2", tSentryPrivilege)
  return HttpResponse()


def revoke_privileges(request):
  tSentryPrivilege = _to_sentry_privilege("ALL")
  result = get_api(request.user, "cdap").alter_sentry_role_revoke_privilege("testrole2", tSentryPrivilege)
  return HttpResponse()


def list_roles_by_group(request):
  sentry_privileges = get_api(request.user, "cdap").list_sentry_roles_by_group()
  #sentry_privileges = [{"name": "testrole2", "groups": []}, {"name": "testrole1", "groups": []}]
  print sentry_privileges
  return HttpResponse(json.dumps(sentry_privileges), content_type="application/json")


def list_privileges_by_role(request, role):
  sentry_privileges = get_api(request.user, "cdap").list_sentry_privileges_by_role("cdap", role)
  print sentry_privileges
  return HttpResponse(json.dumps(sentry_privileges), content_type="application/json")


def list_privileges_by_group(request, group):
  api = get_api(request.user, "cdap")
  # Fetch all the privileges from sentry first
  sentry_privileges = api.list_sentry_roles_by_group()
  #sentry_privileges = [{"name": "testrole2", "groups": []}, {"name": "testrole1", "groups": []}]
  print sentry_privileges

  # Construct a dcitionary like {groupname:[role1,role2,role3]}
  reverse_group_role_dict = dict()
  for item in sentry_privileges:
    role_name = item["name"]
    for g in item["groups"]:
      if g not in reverse_group_role_dict:
        reverse_group_role_dict[g] = []
      reverse_group_role_dict[g].append(role_name)

  response = []
  if group in reverse_group_role_dict:
    for role in reverse_group_role_dict[group]:
      response += api.list_sentry_privileges_by_role("cdap", role)
  return HttpResponse(json.dumps(response), content_type="application/json")


def list_privileges_by_authorizable(request):
  # This is a test
  authorizableSet = [{"authorizables":[{"type":"NAMESPACE", "name":"rohit"}]}]
  sentry_privileges = get_api(request.user, "cdap").list_sentry_privileges_by_authorizable("cdap", authorizableSet)
  return HttpResponse(json.dumps(sentry_privileges), content_type="application/json")
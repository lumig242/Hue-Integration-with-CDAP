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
from django.http import HttpResponse, HttpResponseRedirect, HttpResponse, HttpResponseServerError
from cdap.client import auth_client
from cdap.conf import CDAP_API_HOST, CDAP_API_PORT, CDAP_API_VERSION
from libsentry.api2 import get_api

import urllib2
import json
import logging
from collections import defaultdict

LOG = logging.getLogger(__name__)
# BASE_URL = "http://{}:{}/{}".format(CDAP_API_HOST.get(), CDAP_API_PORT.get(), CDAP_API_VERSION.get())
BASE_URL = "http://hue29208-1000.dev.continuuity.net:10000/v3"
CDAP_CLIENT = auth_client(BASE_URL)
ENTITIES_ALL = dict()


##############################################################
# Localized helper functions defined here
##############################################################

def _call_cdap_api(url):
  return CDAP_CLIENT.get(url)


def _match_authorizables(authorizables, path):
  return True if path[:len(authorizables)] == authorizables else False


def _to_sentry_privilege(action, authorizables):
  return {
    "component": "cdap",
    "serviceName": "cdap",
    "authorizables": authorizables,
    "action": action,
  }


def _path_to_sentry_authorizables(path):
  path = path.strip("/").split("/")
  path = ["instance", "cdap", "namespace"] + path
  return [{"type": path[i].upper(), "name": path[i + 1].lower()} for i in xrange(0, len(path), 2)]


def _sentry_authorizables_to_path(authorizables):
  path = [auth[key] for auth in authorizables for key in ("type", "name")]
  return "/".join(path)


##############################################################
# Router functions goes here
##############################################################

def cdap_authenticate(request):
  """
  API for authentication of CDAP secure clusters
  :param request: POST DATA: {"username":username, "password":password}
  :return:
  """
  try:
    CDAP_CLIENT.set_credentials(request.POST["username"], request.POST["password"])
    return HttpResponse()
  except Exception as e:
    return HttpResponseServerError(e, content_type="application/text")


def index(request):
  global ENTITIES_ALL
  if not CDAP_CLIENT.is_set_credentials:
    return render('index.mako', request, dict(date2="testjson", unauthenticated=True))
  namespace_url = "/namespaces"
  namespaces = _call_cdap_api(namespace_url)
  entities = dict((ns.get("name"), dict()) for ns in namespaces)
  ENTITIES_ALL = dict((ns.get("name"), ns) for ns in namespaces)

  # cdap_rest_apis = {
  #   "stream": "/streams",
  #   "dataset": "/data/datasets",
  #   "artifact": "/artifacts",
  #   "application": "/apps",
  # }
  #
  # for ns in entities:
  #   for entity_type, entity_url in cdap_rest_apis.iteritems():
  #     full_url = namespace_url + "/" + ns + entity_url
  #     items = _call_cdap_api(full_url)
  #
  #     if entity_type == "application":
  #       entities[ns][entity_type] = {}
  #       ENTITIES_ALL[ns][entity_type] = {}
  #       # Application has addtional hierarchy
  #       for item in items:
  #         programs = _call_cdap_api(full_url + "/" + item["name"])["programs"]
  #         program_dict = dict()
  #         for program in programs:
  #           if program["type"] not in program_dict:
  #             program_dict[program["type"].lower()] = list()
  #           program_dict[program["type"].lower()].append(program)
  #         entities[ns][entity_type][item["name"]] = program_dict
  #         ENTITIES_ALL[ns][entity_type][item["name"]] = dict((p_type, {p["name"]: p})
  #                                                            for p_type, programs in program_dict.iteritems()
  #                                                            for p in programs)
  #         ENTITIES_ALL[ns][entity_type][item["name"]].update(item)
  #     else:
  #       entities[ns][entity_type] = [item.get("name") for item in items]
  #       ENTITIES_ALL[ns][entity_type] = dict((item.get("name"), item) for item in items)

  return render('index.mako', request, dict(date2="testjson", entities=entities))


def details(request, path):
  """
  Return detailed information of the entity with path
  :param request:
  :param path: Path to the entity
  :return: Json Struct. Specifically, sentry privileges are constructed as:
  {
    "privileges": {
      "role": {
        "actions": [action1, action2, action3...],
      }
    }
  }
  """
  item = ENTITIES_ALL
  for k in path.strip("/").split("/"):
    item = item[k]

  api = get_api(request.user, "cdap")
  # Fetch all the privileges from sentry first
  roles = [result["name"] for result in api.list_sentry_roles_by_group()]
  privileges = {}
  path = _path_to_sentry_authorizables(path)
  for role in roles:
    sentry_privilege = api.list_sentry_privileges_by_role("cdap", role)
    for privilege in sentry_privilege:
      if _match_authorizables(privilege["authorizables"], path):
        if role not in privileges:
          privileges[role] = defaultdict(list)
        privileges[role]["actions"].append(privilege["action"])


  item["privileges"] = privileges
  return HttpResponse(json.dumps(item), content_type="application/json")


def grant_privileges(request):
  """
  Grant a list of actions to an entity. Should be a Post Method.
  :param request: POST DATA{
    "role":role name of,
    "actions": a list/array of actions,
    "path": the path to entity,
  }
  """
  api = get_api(request.user, "cdap")
  role = request.POST["role"]
  actions = request.POST.getlist("actions[]")
  authorizables = _path_to_sentry_authorizables(request.POST["path"])
  for action in actions:
    tSentryPrivilege = _to_sentry_privilege(action, authorizables)
    api.alter_sentry_role_grant_privilege(role, tSentryPrivilege)
  return HttpResponse()


def revoke_privileges(request):
  """
  Revoke a list of actions to an entity. Should be a Post Method.
  :param request: POST DATA{
    "role":role name of,
    "actions": a list/array of actions,
    "path": the path to entity,
  }
  :return: If entity privileges cannot be revoked, return a Json array of where these privileges are defined.
  """
  api = get_api(request.user, "cdap")
  role = request.POST["role"]
  actions = request.POST.getlist("actions[]")
  authorizables = _path_to_sentry_authorizables(request.POST["path"])
  for action in actions:
    tSentryPrivilege = _to_sentry_privilege(action, authorizables)
    api.alter_sentry_role_revoke_privilege(role, tSentryPrivilege)
  # Check if all the privileges are revoked successfully
  response_msgs = [_sentry_authorizables_to_path(priv["authorizables"])
                   for priv in api.list_sentry_privileges_by_role("cdap", role)
                   if _match_authorizables(priv["authorizables"], authorizables)]
  return HttpResponse(json.dumps(response_msgs), content_type="application/json")


def list_roles_by_group(request):
  """
  List sentry roles along with group
  :param request:
  :return: A Json struct
    {
      "name": role name,
      "groups": [group1, group2, group3...]
    }
  """
  sentry_privileges = get_api(request.user, "cdap").list_sentry_roles_by_group()
  return HttpResponse(json.dumps(sentry_privileges), content_type="application/json")


def list_privileges_by_role(request, role):
  """
  List sentry privilegs by role
  :param request:
  :param role: role name
  :return: A Json array of SentryPrivileges: [p1, p2, p3...]
  """
  sentry_privileges = get_api(request.user, "cdap").list_sentry_privileges_by_role("cdap", role)
  return HttpResponse(json.dumps(sentry_privileges), content_type="application/json")


def list_privileges_by_group(request, group):
  """
  List sentry privileges by group
  :param request:
  :param group: group name
  :return: A Json array of SentryPrivileges: [p1, p2, p3...]
  """
  api = get_api(request.user, "cdap")
  sentry_privileges = api.list_sentry_roles_by_group()
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
  """
  A test function
  :param request:
  :return:
  """
  authorizableSet = [{"authorizables": [{"type": "NAMESPACE", "name": "rohit"}]}]
  sentry_privileges = get_api(request.user, "cdap").list_sentry_privileges_by_authorizable("cdap", authorizableSet)
  return HttpResponse(json.dumps(sentry_privileges), content_type="application/json")


def create_role(request, role_name):
  """

  :param request:
  :param role_name:
  :return:
  """
  get_api(request.user, "cdap").create_sentry_role(role_name)
  return HttpResponse()


def drop_role(request, role_name):
  """

  :param request:
  :param role_name:
  :return:
  """
  get_api(request.user, "cdap").drop_sentry_role(role_name)
  return HttpResponse()

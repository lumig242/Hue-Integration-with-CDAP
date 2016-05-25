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
from conf import CDAP_API_HOST, CDAP_API_PORT, CDAP_API_VERSION

import urllib2
import json

#BASE_URL = "http://{}:{}/{}".format(CDAP_API_HOST.get(), CDAP_API_PORT.get(), CDAP_API_VERSION.get())
BASE_URL = "http://127.0.0.1:10000/v3"
ENTITIES_ALL = dict()

def _call_cdap_api(url):
  return json.loads(urllib2.urlopen(BASE_URL + url).read())


def index(request):
  global ENTITIES_ALL
  namespace_url = "/namespaces"
  namespaces = _call_cdap_api(namespace_url)
  entities = {ns.get("name"):dict() for ns in namespaces}
  ENTITIES_ALL = {ns.get("name"):ns for ns in namespaces}

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
          ENTITIES_ALL[ns][entity_type][item["name"]] = {p_type:{p["name"]:p}
                                                         for p_type, programs in program_dict.items()
                                                          for p in programs}
          ENTITIES_ALL[ns][entity_type][item["name"]].update(item)
      else:
        entities[ns][entity_type] = [item.get("name") for item in items]
        ENTITIES_ALL[ns][entity_type] = {item.get("name"): item for item in items}


  print entities
  print ENTITIES_ALL
  return render('index.mako', request, dict(date2="testjson", entities=entities))


def details(request, path):
  item = ENTITIES_ALL
  for k in path.strip("/").split("/"):
    item = item[k]
  return HttpResponse(json.dumps(item).replace("\n", ""), content_type="application/json")
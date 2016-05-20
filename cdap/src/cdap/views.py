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

def _call_api(url):
  return json.loads(urllib2.urlopen(BASE_URL + url).read())


def index(request):
  print "="*50 + BASE_URL
  entities = dict()
  namespace_url = "/namespaces"
  stream_url = "/streams"
  dataset_url = "/data/datasets"

  namespaces = _call_api(namespace_url)
  entities = {ns.get("name"):dict() for ns in namespaces}
  for ns in entities:
    streams = _call_api(namespace_url + "/" + ns + stream_url)
    entities[ns]["streams"] = [stream.get("name") for stream in streams]
    datasets = _call_api(namespace_url + "/" + ns + dataset_url)
    entities[ns]["datasets"] = [dataset.get("name") for dataset in datasets]

  return render('index.mako', request, dict(date2="testjson", entities=entities))


def namespaces(request, namespace_id):
  try:
    namespace_info = json.loads(urllib2.urlopen(BASE_URL + "/namespaces/" + namespace_id).read())
    return HttpResponse(json.dumps(namespace_info), content_type="application/json")
  except urllib2.HTTPError:
    return HttpResponse("", content_type="application/json")




import requests
import json


class auth_client:
  def __init__(self, host_url="0.0.0.0:10000/v3"):
    self.host_url = host_url
    self.auth_header = None
    self._cdap_username = None
    self._cdap_password = None
    self.is_set_credentials = False

  def set_credentials(self, username, password):
    self._cdap_username = username
    self._cdap_password = password
    self.is_set_credentials = True

  def get_token(self, auth_uri):
    return json.loads(requests.get(auth_uri, auth=(self._cdap_username, self._cdap_password)).content)


  def get(self, url):
    res = json.loads(requests.get(self.host_url + url, headers=self.auth_header).text)
    if "auth_uri" in res:
      # Not authorized/ Expired
      # Update the token
      token = self.get_token(res["auth_uri"][0])
      print token
      self.auth_header = {'Authorization': token["token_type"] + ' ' + token["access_token"]}
      res = json.loads(requests.get(self.host_url + url, headers=self.auth_header).text)
    return res

if __name__ == "__main__":
  client = auth_client("http://hue-security9535-1000.dev.continuuity.net:10000/v3")
  print client.get("/namespaces")

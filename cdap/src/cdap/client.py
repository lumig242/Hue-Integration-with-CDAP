import requests
import json
import re


class auth_client:
  """
  An authorization Client to connect to CDAP restservice running on a secure cluster
  """

  def __init__(self, host_url="0.0.0.0:10000/v3"):
    self.host_url = host_url
    self.auth_header = None
    self._cdap_username = None
    self._cdap_password = None
    self.is_set_credentials = False

  def set_credentials(self, username, password):
    self._cdap_username = username
    self._cdap_password = password
    try:
      self.get("/namespaces")
      self.is_set_credentials = True
    except requests.exceptions.ConnectionError:
      raise Exception("Cannot decode the reponse from host. Please check your cdap host settings.")

  def get_token(self, auth_uri):
    try:
      response = requests.get(auth_uri, auth=(self._cdap_username, self._cdap_password)).content
      return json.loads(response)
    except ValueError:
      # Fail to fetch the token.
      error_title = re.findall("<title>(.*?)</title>", response)[0]
      raise Exception(error_title + "; Maybe check your username and password for cdap security cluster.")

  def get(self, url):
    try:
      res = json.loads(requests.get(self.host_url + url, headers=self.auth_header).text)
    except ValueError:
      # If cannot decode json object here means wrong URL endpoint is set
      raise Exception("Cannot decode the reponse from host. Please check your cdap host settings.")
    if "auth_uri" in res:
      # Not authorized/ Expired
      # Update the token
      token = self.get_token(res["auth_uri"][0])
      self.auth_header = {'Authorization': token["token_type"] + ' ' + token["access_token"]}
      res = json.loads(requests.get(self.host_url + url, headers=self.auth_header).text)
    return res


if __name__ == "__main__":
  client = auth_client("http://rohit9692-1000.dev.continuuity.net:100000/v3")
  client.set_credentials("", "")

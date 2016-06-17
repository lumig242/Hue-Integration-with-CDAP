from cdap.client import auth_client
from cdap.conf import CDAP_API_HOST, CDAP_API_PORT, CDAP_API_VERSION

import re


class test_auth_client_api:
  def test_set_credentials(self):
    """
    Give correct credentials
    :return:
    """
    STRIPPED_CDAP_API_HOST = re.sub("^http://", "", CDAP_API_HOST.get())
    client = auth_client(STRIPPED_CDAP_API_HOST, CDAP_API_PORT.get(), CDAP_API_VERSION.get())
    client.authenticate("shenggu", "udxc2knu")
    assert client.is_set_credentials == True
    assert type(client.get("/namespaces")) == list


  def test_set_credentials_incorrect(self):
    """
    Test incorrect credentials
    :return:
    """
    STRIPPED_CDAP_API_HOST = re.sub("^http://", "", CDAP_API_HOST.get())
    client = auth_client(STRIPPED_CDAP_API_HOST, CDAP_API_PORT.get(), CDAP_API_VERSION.get())
    try:
      client.authenticate("wrong_username", "wrong_password")
    except Exception as e:
      # Should return 401 unauthorized error
      assert "401" in str(e)
    assert client.is_set_credentials == False


  def test_set_credentials_wrong_host(self):
    """
    Test incorrect credentials
    :return:
    """
    client = auth_client("http://non-existing.host.com", 6666, "v3")
    try:
      client.authenticate("shenggu", "udxc2knu")
    except Exception as e:
      # Should inform hostname error
      assert "[Errno 8] nodename nor servname provided, or not known" in str(e)
    assert client.is_set_credentials == False



import requests
from desktop.lib.django_test_util import make_logged_in_client

class test_rest_apis:
  def __init__(self):
    self.client = make_logged_in_client(username="test", password="test", is_superuser=True)

  def test_another(self):
    response = self.client.get("/cdap/list_roles_by_group")
    print response.content
    print response
    assert False
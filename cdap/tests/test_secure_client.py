from cdap.src.cdap.client import auth_client

# The base url of cdap rest service
BASE_URL = "http://rohit9692-1000.dev.continuuity.net:10000/v3"


def test_set_credentials():
  """
  Give correct credentials
  :return:
  """
  client = auth_client(BASE_URL)
  client.set_credentials("shenggu", "udxc2knu")
  assert client.is_set_credentials == True
  assert type(client.get("/namespaces")) == list


def test_set_credentials_incorrect():
  """
  Test incorrect credentials
  :return:
  """
  client = auth_client(BASE_URL)
  try:
    client.set_credentials("wrong_username", "wrong_password")
  except Exception as e:
    assert "401 Unauthorized" in e.message
  assert client.is_set_credentials == False


def test_set_credentials_wrong_host():
  """
  Test incorrect credentials
  :return:
  """
  FAKE_URL = "http://non-existing.host.com:6666"
  client = auth_client(FAKE_URL)
  try:
    client.set_credentials("shenggu", "udxc2knu")
  except Exception as e:
    assert "Please check your cdap host settings" in e.message
  assert client.is_set_credentials == False

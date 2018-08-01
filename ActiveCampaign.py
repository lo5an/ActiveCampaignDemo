from pprint import pprint
import requests
import time
import datetime
import yaml
import sys

class ActiveCampaignApi:
  """Simple  object for interacting with the Active Campaign API.
  Args:
    ac_url : active campaign api url
    ac_key : active campaign key
  """

  def __init__(self, ac_url, ac_key):
    self.ac_url = ac_url
    self.ac_key = ac_key

  def post(self, action, ac_body={}):
    """ Send an action and specified body values to the Active Campaign API.
    Args:
       action : a valid Active Campaign api_action parameter
       body   : other paramaters needed for that action
    """
    ac_body['api_action'] = action
    ac_body['api_key'] = self.ac_key
    ac_body['api_output'] = 'json'
    r = requests.post(self.ac_url, data=ac_body)
    return r.json()
  
  def create_test_address(self, ): 
    """"Add some test123  addresses
    """  
 
    # Noop if we already have an address
    r = self.post("address_list")
    if '0' in r:
      return
  
    address_data = {
      "company_name" : "Test Company",
      "address_1"    : "1234 Test Blvd",
      "city"         : "Norman",
      "state"        : "Oklahoma",
      "zip"          : "73069",
      "country"       : "US",
    }
    r = self.post("address_add", address_data)
  
  def create_test_list(self):
    """ Make sure we have a test list to send from
    """
    test_list = False
    list_data = {'ids': 'all', 
       'filters[name]': 'Test List'}
    r = self.post('list_list', list_data)
    if 1 == r['result_code']:
      test_list = r['0']['id']
    if 0 == r['result_code']:
      list_data = {
        'name': 'Test List', 
        'sender_name': 'Test Company', 
        'sender_addr1': '123 Test Blvd', 
        'sender_zip': '73069', 
        'sender_city': 'Norman', 
        'sender_country': 'US', 
        'sender_url': 'https://vlrst.com', 
        'sender_reminder': "You are one of my test addresses"
      }
      r = self.post('list_add', list_data)
      test_list = r['id']
    return test_list
  
  def populate_test_contacts(self, list_id):
    """Add a few test123 contacts.
    Args
      list_id : attach test contacts to list
    """
    for i in range(0,5):
      contact_data = {
          "first_name"    : "Testy",
          "last_name"     : "McTest%s" % str(i),
          "email"         : "test123+%s@vlrst.com" % str(i),
          "tags"          : "test",
          "p[%s]"%list_id : list_id
      }
      r = self.post("contact_sync", contact_data) 
  
  def create_test_message (self, list_id, tag):
    """ Create a plain text test message
    Args:
      list_id : send message to list
      tag : identifier string for message
    """
  
    message_data = {
       "format"    : "text",
       "subject"   : "Test Message %s" % tag,
       "fromemail" : "test123@vlrst.com",
       "fromname"  : "Testy McTest",
       "reply2"    : "test234@vlrst.com",
       "priority"  : "3",
       "charset"   : "utf8",
       "encoding"  : "quoted-printable",
       "text"      : "This is a test!",
       "p[%s]"%list_id : list_id
    }
    r = self.post("message_add", message_data)
    return r['id']
  
  
  def send_test_campaign(self, list_id, message_id, tag):
    """ Send out a test message to a test campaign
    Args:
      list_id    : list to send message
      message_id : previously created test message
      tag        : label to apply to campaign
    """
    # sdate seems to want to be a future time to make sure sending gets triggered
    sdate_tuple = ( datetime.datetime.now() + datetime.timedelta(minutes = 2)).timetuple()
    sdate = time.strftime('%Y-%m-%d %H:%M:%S', sdate_tuple)
  
    campaign_data = {
      "type"       : "single",
      "name"       : "Test Campaign %s" % tag,
      "sdate"      : sdate,
      "status"     : "1",
      "public"     : "0",
      "tracklinks" : "0", 
      "p[%s]" % list_id    : list_id,
      "m[%s]" % message_id : 100,
    }
    r = self.post("campaign_create", campaign_data)
    print("Created and scheduled campaign %s" % r['id'])


if __name__ =="__main__": 

  # Did we call the script correctly?
  if len(sys.argv) < 2:
      print("Please specify a file with credentials as the script argument.")
      sys.exit(1)

  # Read in config
  secrets_file = sys.argv[1]
  ac_config = yaml.safe_load(open(secrets_file))
  ac_url = ac_config ["ac_url"]
  ac_key = ac_config ["ac_key"]

  # Set up to send to send test campaign
  ac_api = ActiveCampaignApi(ac_url, ac_key)
  ac_api.create_test_address()
  list_id = ac_api.create_test_list()
  ac_api.populate_test_contacts(list_id)

  # Create and send test message
  tag = int(time.time())
  message_id = ac_api.create_test_message(list_id, tag)
  ac_api.send_test_campaign(list_id, message_id, tag)

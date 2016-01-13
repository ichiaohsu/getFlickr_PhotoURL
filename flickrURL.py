import urllib
import oauth
import hidden
import re
import json
#request_token_url = "http://www.flickr.com/services/oauth/request_token"
authorize_url = "http://www.flickr.com/services/oauth/authorize"
access_token_url = "http://www.flickr.com/services/oauth/access_token"

def init_secrets():
	
	keyholds = hidden.keys()
	keyholds["oauth_timestamp"] = oauth.generate_timestamp()
	keyholds["oauth_nonce"] = oauth.generate_nonce()

	return keyholds

def get_user(url):
	
	secrets = init_secrets()

	# Setup the consumer with api_key and api_secret
	consumer = oauth.OAuthConsumer(secrets["oauth_consumer_key"], secrets["oauth_consumer_secret"])
	# Create request
	oauth_req = oauth.OAuthRequest(http_method="GET", http_url=url, parameters=secrets)
	# Create signature
	oauth_req.sign_request(oauth.OAuthSignatureMethod_HMAC_SHA1(),consumer, None)

	#print "secrets: ", secrets
	#return oauth_req.to_url()
	url = oauth_req.to_url()
	
	print '* Calling Flickr...'
	connection = urllib.urlopen(url)
	data = connection.read()

	request_token = {
    	"oauth_token": re.findall("oauth_token=(.+)&",data)[0],
    	"oauth_token_secret": re.findall("oauth_token_secret=(.+)", data)[0]
    }
    #print "Request Token:"
    #print " - oauth_token = %s" % request_token['oauth_token']
    #print " - oauth_token_secret = %s" % request_token['oauth_token_secret']
    #print

	token = oauth.OAuthToken(request_token["oauth_token"], request_token['oauth_token_secret'])

	print "Go to the following link in your browser:"
	print "%s?oauth_token=%s&perms=read" %(authorize_url, request_token['oauth_token'])

	oauth_verifier = raw_input("Enter the verifier - ")

	secrets["oauth_token"] = request_token["oauth_token"]
	secrets["oauth_verifier"] = oauth_verifier

	print secrets
	print

	del secrets["oauth_consumer_secret"]

	oauth_req = oauth.OAuthRequest(http_method="GET", http_url=access_token_url, parameters=secrets)
	oauth_req.sign_request(oauth.OAuthSignatureMethod_HMAC_SHA1(),consumer, token)

	url = oauth_req.to_url()
	connection = urllib.urlopen(url)
	data = connection.read()

	print "data: ", data
	print

	secrets["oauth_token"] = re.findall("oauth_token=(.+?)&", data)[0]
	secrets["oauth_token_secret"] = re.findall("oauth_token_secret=(.+?)&", data)[0]
	secrets["username"] = re.findall("username=(.+)",data)[0]
	secrets["user_nsid"] = re.findall("user_nsid=(.+?)&",data)[0]
	"""
	user = {
		"user_nsid": re.findall("user_nsid=(.+?)&",data)[0],
		"username": re.findall("username=(.+)",data)[0],
		"oauth_token": re.findall("oauth_token=(.+?)&", data)[0],
		"oauth_token_secret": re.findall("oauth_token_secret=(.+?)&", data)[0]
	}"""

	#print user
	return secrets


def get_Photosets_list(api_url, params):
	

	urlprms = {
		"method": "flickr.photosets.getList",
		"api_key": params["oauth_consumer_key"],
		"user_id": params["user_nsid"],
		"format": "json",
		"nojsoncallback": "1",
		"auth_token": params["oauth_token"],
		"api_sig": params["oauth_signature"]
	}

	url = api_url + urllib.urlencode(urlprms)
	print "photosets url: ", url
	print

	data = urllib.urlopen(url).read()

	print data
	print

	js = json.loads(data)

	print js
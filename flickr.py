#Class base flickr module
import urllib
import hidden
import oauth
import re
import json

def getToken():
	result = dict()

	fp = open("token")

	result["token"] = fp.readline().rstrip('\n')
	result["token_secret"] = fp.readline()
	
	fp.close()
	return result

class flickrInit(object):

	keys = dict()
	tokens = dict()

	def __init__(self):
		
		#init defaults
		self.keys = hidden.keys()
		self.url = "http://api.flickr.com/services/rest"

	def get_Tokens(self, url):

		defaults = hidden.keys()
		defaults["oauth_timestamp"] = oauth.generate_timestamp()
		defaults["oauth_nonce"] = oauth.generate_nonce()
		defaults["oauth_signature_method"] = "HMAC-SHA1"
		defaults["oauth_version"] = "1.0"
		defaults["oauth_callback"] = "http://ichiaohsu.github.io"

		#print "asking: " , url, "params= ", defaults

		# Setup the consumer with api_key and api_secret
		consumer = oauth.OAuthConsumer(defaults["oauth_consumer_key"], defaults["oauth_consumer_secret"])
		# Create request
		oauth_req = oauth.OAuthRequest(http_method="GET", http_url=url, parameters=defaults)
		# Create signature
		oauth_req.sign_request(oauth.OAuthSignatureMethod_HMAC_SHA1(),consumer, None)

		url = oauth_req.to_url()
	
		print '* Calling Flickr...'
		connection = urllib.urlopen(url)
		data = connection.read()
		
		print data
		
		request_token = {
			"oauth_token": re.findall("oauth_token=(.+)&",data)[0],
			"oauth_token_secret": re.findall("oauth_token_secret=(.+)",data)[0]
		}

		print request_token
		token = oauth.OAuthToken(request_token["oauth_token"], request_token["oauth_token_secret"])

		print "Go to the following link in your browser:"
		print "http://www.flickr.com/services/oauth/authorize?oauth_token=%s&perms=read" % request_token['oauth_token'] 
		print

		oauth_verifier = raw_input("Enter the verifier - ")
		defaults["oauth_token"] = request_token["oauth_token"]
		defaults["oauth_verifier"] = oauth_verifier

		del defaults["oauth_consumer_secret"]
		
		oauth_req = oauth.OAuthRequest(http_method="GET", http_url="http://www.flickr.com/services/oauth/access_token", parameters=defaults)
		oauth_req.sign_request(oauth.OAuthSignatureMethod_HMAC_SHA1(),consumer, token)

		url = oauth_req.to_url()
		connection = urllib.urlopen(url)
		data = connection.read()

		print "data: ", data
		print

		defaults["oauth_token"] = re.findall("oauth_token=(.+?)&", data)[0]
		defaults["oauth_token_secret"] = re.findall("oauth_token_secret=(.+?)&", data)[0]
		defaults["username"] = re.findall("username=(.+)",data)[0]
		defaults["user_nsid"] = re.findall("user_nsid=(.+?)&",data)[0]

		print defaults
		print

		self.tokens["oauth_token"] = defaults["oauth_token"]
		self.tokens["oauth_token_secret"] = defaults["oauth_token_secret"]

		with open('token', 'w') as f:
			f.write(self.tokens['oauth_token'] + '\n')
			f.write(self.tokens['oauth_token_secret'])
		f.closed

	def get_keys(self):
		print "keys:", self.keys
		return self.keys

	def get_tokens(self):
		print "tokens: ", self.tokens
	
class photosets(object):

	def __init__(self, nojsoncallback=True, format='json', parameters=None):

		self.keys = hidden.keys()
		self.tokenfile = getToken()

		print self.keys
		print self.tokenfile

		self.consumer = oauth.OAuthConsumer(self.keys["oauth_consumer_key"], self.keys["oauth_consumer_secret"])
		self.token = oauth.OAuthToken(self.tokenfile["token"], self.tokenfile["token_secret"])

		if nojsoncallback:
			self.nojsoncallback = 1
		else:
			self.nojsoncallback = 0
		if not parameters:
			parameters = {}

		self.url = "https://api.flickr.com/services/rest"

		defaults = {
			"format": format,
			"nojsoncallback": self.nojsoncallback,
			"oauth_timestamp": oauth.generate_timestamp(),
			"oauth_nonce": oauth.generate_nonce(),
			"signature_method": "HMAC-SHA1",
			"oauth_token": self.token.key,
			"api_key": self.consumer.key
		}

		#print "defaults: ", defaults

		self.parameters = defaults
	
	def get_setid_user(self, user_id,page, per_):

		params = self.parameters.copy()
		#print "d: ", d

		params.update({
			"method": "flickr.photosets.getList",
			"user_id": user_id
		})

		#print "self:", self.parameters
		#print "d:", d
		req = oauth.OAuthRequest(http_method="GET", http_url=self.url, parameters=d)
		req.sign_request(oauth.OAuthSignatureMethod_HMAC_SHA1(),self.consumer, self.token)

		url = req.to_url()
		print "url:", url
		data = urllib.urlopen(url).read()
		print data

	def get_photoSize_Byid(self, photo_id, size=0):

		params = self.parameters.copy()

		#update request variables
		params.update({
			"method": "flickr.photos.getSizes",
			"photo_id": str(photo_id)
		})
		#request call
		req = oauth.OAuthRequest(http_method="GET", http_url=self.url, parameters=params)
		req.sign_request(oauth.OAuthSignatureMethod_HMAC_SHA1(),self.consumer, self.token)

		url = req.to_url()
		data = urllib.urlopen(url).read()

		js = json.loads(data)
		
		# Handle fail situation
		if js["stat"] == "fail":
			print "get size url fail."
		elif js["stat"] == "ok":
			for item in js["sizes"]["size"]:
				if int(item["width"]) == size and size != 0:
					result_url = item["source"]
			else:
				return result_url

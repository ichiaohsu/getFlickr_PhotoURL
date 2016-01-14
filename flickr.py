#Class base flickr module
import urllib
import hidden
import oauth
import re
import json

class flickrAPI(object):

	keys = dict()
	tokens = dict()
	apitokens = dict()

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

		self.apitokens["oauth_token"] = defaults["oauth_token"]
		self.apitokens["oauth_token_secret"] = defaults["oauth_token_secret"]

	def get_info(self):
		print "keys:", self.keys
		print "tokens: ", self.apitokens
	
	"""
	def set_Method(self,nojsoncallback=True,format='json',parameters=None):

		self.consumer = oauth.OAuthConsumer(self.keys["oauth_consumer_key"], self.keys["oauth_consumer_secret"])
		self.tokens = oauth.OAuthToken(self.apitokens["oauth_token"], self.apitokens["oauth_token_secret"])
		print "self.consumer: ", self.consumer
		print "self.tokens: ", self.tokens

		if nojsoncallback:
			self.nojsoncallback = 1
		else:
			self.nojsoncallback = 0
		if not parameters:
			parameters = {}

        #self.url = "http://api.flickr.com/services/rest"

        
        defaults = {
            'format':format,
            'nojsoncallback':self.nojsoncallback,
            'signature_method': "HMAC-SHA1",
            'oauth_token':self.tokens.key,
            'oauth_consumer_key':self.consumer.key,
        }

        defaults.update(parameters)
        self.parameters = defaults

    def flickr_calls(self):
    	uniques = {
    		"oauth_timestamp": oauth.generate_timestamp(),
    		"oauth_nonce": oauth.generate_nonce()
    		}

    	self.parameters.update(uniques)
    	#req = oauth.Request(method="GET", url=self.url, parameters=self.parameters)
    	req = oauth.OAuthRequest(http_method="GET", http_url=self.url, parameters=self.parameters)
    	# Create signature
    	req.sign_request(oauth.OAuthSignatureMethod_HMAC_SHA1(),self.consumer, self.tokens)
    	req_url = req.to_url()
    	data = urllib.urlopen(req_url).read()
    	
    	print data

"""
#Class base flickr module
import urllib
import hidden
import oauth
import re
import json
import sqlite3

# open flickruser.sqlite
conn = sqlite3.connect("flickr.db")
cur = conn.cursor()

class login(object):

	keys = dict()
	tokens = dict()

	def __init__(self,username):
		# Set up token url
		self.url_req_token = "http://www.flickr.com/services/oauth/request_token"
		self.url_access_token = "http://www.flickr.com/services/oauth/access_token"

		# Set up app keys
		self.keys = hidden.keys()

		try:
			cur.execute('''SELECT token_id FROM Users WHERE name = ? ''',(username, ) )
			token_id = cur.fetchone()[0]
			print token_id

			cur.execute('''SELECT token, secret FROM Tokens WHERE id = ?''',(token_id, ) )
			result = cur.fetchone()
			#print result

			self.tokens["token"] = result[0]
			self.tokens["token_secret"] = result[1]

		# Should specify sqlite table not exist error later in except part
		except sqlite3.OperationalError:
			print "Username not found in database. Re-initialize user authorization..."
			print

			# Table not exist in database, CREATE TABLE Users and Tokens
			cur.executescript('''
			CREATE TABLE Users(
				id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
				name TEXT UNIQUE,
				token_id INTERGER
			);
			CREATE TABLE Tokens(
				id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
				token TEXT,
				secret TEXT
			);
			''')

			self.user_authorize()

		"""
		try:
			fi = open("token","r")

			self.tokens["token"] = fi.readline().rstrip('\n')
			self.tokens["token_secret"] = fi.readline()

			fi.close()

		except IOError:
			print "Token inexist. Re-initialize user authorization..."
			print
			self.user_authorize()
		"""

	def user_authorize(self):

		defaults = hidden.keys().copy()
		defaults["oauth_timestamp"] = oauth.generate_timestamp()
		defaults["oauth_nonce"] = oauth.generate_nonce()
		defaults["oauth_signature_method"] = "HMAC-SHA1"
		defaults["oauth_version"] = "1.0"
		defaults["oauth_callback"] = "https://www.flickr.com/"

		# Setup the consumer with api_key and api_secret
		consumer = oauth.OAuthConsumer(defaults["oauth_consumer_key"], defaults["oauth_consumer_secret"])
		# Create request
		oauth_req = oauth.OAuthRequest(http_method="GET", http_url=self.url_req_token, parameters=defaults)
		# Create signature
		oauth_req.sign_request(oauth.OAuthSignatureMethod_HMAC_SHA1(),consumer, None)

		url = oauth_req.to_url()
	
		print '* Calling Flickr...'
		connection = urllib.urlopen(url)
		data = connection.read()
		
		#print data
		
		request_token = {
			"oauth_token": re.findall("oauth_token=(.+)&",data)[0],
			"oauth_token_secret": re.findall("oauth_token_secret=(.+)",data)[0]
		}

		#print request_token
		token = oauth.OAuthToken(request_token["oauth_token"], request_token["oauth_token_secret"])

		print "Go to the following link in your browser:"
		print "http://www.flickr.com/services/oauth/authorize?oauth_token=%s&perms=read" % request_token['oauth_token'] 
		print

		oauth_verifier = raw_input("Enter the verifier - ")
		print

		defaults["oauth_token"] = request_token["oauth_token"]
		defaults["oauth_verifier"] = oauth_verifier

		del defaults["oauth_consumer_secret"]
		
		oauth_req = oauth.OAuthRequest(http_method="GET", http_url=self.url_access_token, parameters=defaults)
		oauth_req.sign_request(oauth.OAuthSignatureMethod_HMAC_SHA1(),consumer, token)

		url = oauth_req.to_url()
		connection = urllib.urlopen(url)
		data = connection.read()

		#print "data: ", data
		#print

		defaults["oauth_token"] = re.findall("oauth_token=(.+?)&", data)[0]
		defaults["oauth_token_secret"] = re.findall("oauth_token_secret=(.+?)&", data)[0]
		defaults["username"] = re.findall("username=(.+)",data)[0]
		defaults["user_nsid"] = re.findall("user_nsid=(.+?)&",data)[0]

		#print defaults
		#print

		self.tokens["token"] = defaults["oauth_token"]
		self.tokens["token_secret"] = defaults["oauth_token_secret"]

		cur.execute('''INSERT INTO Tokens (token, secret) VALUES (?, ?)''', 
			(defaults["oauth_token"], defaults["oauth_token_secret"]) )
		
		#cur.execute('SELECT id FROM Tokens WHERE token = ?', (defaults["oauth_token"], ) )
		# Named placeholders style
		cur.execute('SELECT id FROM Tokens WHERE token=:t AND secret=:ts', {"t":defaults["oauth_token"], "ts":defaults["oauth_token_secret"]} )
		token_id = cur.fetchone()[0]

		# Store username in database
		cur.execute('''INSERT OR IGNORE INTO Users (name, token_id) VALUES (?, ?)''',(defaults["username"], token_id) )
		#cur.execute('SELECT id FROM Users WHERE name = ?', (defaults["username"], ) )
		#user_id = cur.fetchone()[0]
		#print "user: ", defaults["username"], " id: ", user_id

		conn.commit()
		"""
		with open("token", 'w') as f:
			f.write(self.tokens['token'] + '\n')
			f.write(self.tokens['token_secret'])
		f.closed
		"""

	def get_usertokens(self):
		return self.tokens

	def get_appkeys(self):
		return self.keys

class photosets(object):

	def __init__(self, nojsoncallback=True, format='json', parameters=None):

		self.keys = hidden.keys()
		self.tokenfile = getToken()
		
		if self.tokenfile is not None:

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

			self.parameters = defaults
	
		else:
			print "token is none"
	def make_request(self,parameter=None):
		
		req = oauth.OAuthRequest(http_method="GET", http_url=self.url, parameters=parameter)
		req.sign_request(oauth.OAuthSignatureMethod_HMAC_SHA1(),self.consumer, self.token)

		url = req.to_url()
		
		return url

	def get_photoset_List(self, user_id, page = 1, per_page = 1):

		params = self.parameters.copy()

		params.update({
			"method": "flickr.photosets.getList",
			"user_id": user_id,
			"page": page,
			"per_page": per_page
		})
		
		url = self.make_request(params)
		#print url
		data = urllib.urlopen(url).read()

		js = json.loads(data)
		
		if js["stat"] == "fail":
			print "Fail Code: ", js["code"], " Message: ", js["message"]
		elif js["stat"] == "ok":	#Successful
			result = list()

			for item in js["photosets"]["photoset"]:
				result.append({
					"id": item["id"],
					"title": item["title"]["_content"],
					"description": item["description"]["_content"]
				})
		
			return result

	def get_photolist_from_setid(self, user_id, photo_id):
		
		params = self.parameters.copy()
		
		params.update({
			"method": "flickr.photosets.getPhotos",
			"user_id": user_id,
			"photoset_id": photo_id
		})

		url = self.make_request(params)
		data = urllib.urlopen(url).read()
		js = json.loads(data)

		if js["stat"] == "fail":
			print "Fail Code: ", js["code"], " Message: ", js["message"]
		elif js["stat"] == "ok":	#Successful
		
			photoset = dict()
			photoset["title"] = js["photoset"]["title"]
			photoset["photo"] = list()

			for item in js["photoset"]["photo"]:
				photoset["photo"].append({
					"title": item["title"],
					"id": item["id"]
				})
			return photoset

	def get_photoSize_URL_photoid(self, photo_id, size=0):

		params = self.parameters.copy()

		# Update request variables
		params.update({
			"method": "flickr.photos.getSizes",
			"photo_id": str(photo_id)
		})
		# Request call
		url = self.make_request(params)
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

# -*- coding: utf8 -*-
#Class base flickr module
import urllib
import hidden
import oauth
import re
import json
import sqlite3


# open flickruser.sqlite
conn = sqlite3.connect("flickr.sqlite")
cur = conn.cursor()

class login(object):

	keys = dict()
	tokens = dict()

	# Get User info during init. If user doesn't exist, re-login
	def __init__(self,username):
		# Set up token url
		self.url_req_token = "http://www.flickr.com/services/oauth/request_token"
		self.url_access_token = "http://www.flickr.com/services/oauth/access_token"

		# Set up app keys
		self.keys = hidden.keys()

		# Initialization of database
		self.db_init()

		cur.execute('''SELECT user_id,token_id FROM Users WHERE name = ? ''',(username, ) )

		user_result = cur.fetchone()
		print  user_result
		print

		if user_result is None:

			print "Username not found in database. Re-initialize user authorization..."
			print
			self.user_authorize()
		else:
			print "User logged before. Auto log-in......"
			print
			self.user_id = user_result[0]

			token_id = user_result[1]
			cur.execute('''SELECT token, secret FROM Tokens WHERE id = ?''',(token_id, ) )
			result = cur.fetchone()

			self.tokens["token"] = result[0]
			self.tokens["token_secret"] = result[1]

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
		print
		connection = urllib.urlopen(url)
		data = connection.read()

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

		defaults["oauth_token"] = re.findall("oauth_token=(.+?)&", data)[0]
		defaults["oauth_token_secret"] = re.findall("oauth_token_secret=(.+?)&", data)[0]
		defaults["username"] = re.findall("username=(.+)",data)[0]
		defaults["user_nsid"] = re.findall("user_nsid=(.+?)&",data)[0]

		self.tokens["token"] = defaults["oauth_token"]
		self.tokens["token_secret"] = defaults["oauth_token_secret"]

		# Replace %40 in user_id, or the request url would be wrong
		if "%40" in defaults["user_nsid"]:
			self.user_id = defaults["user_nsid"].replace("%40","@")
			print self.user_id
		else:
			self.user_id = defaults["user_nsid"]

		cur.execute('''INSERT INTO Tokens (token, secret) VALUES (?, ?)''',
			(defaults["oauth_token"], defaults["oauth_token_secret"]) )

		# Named placeholders style
		cur.execute('SELECT id FROM Tokens WHERE token=:t AND secret=:ts', {"t":defaults["oauth_token"], "ts":defaults["oauth_token_secret"]} )
		token_id = cur.fetchone()[0]

		# Store username in database
		cur.execute('''
			INSERT OR IGNORE INTO Users (name, token_id, user_id) VALUES (?, ?, ?)'''
			,(defaults["username"], token_id, self.user_id) )

		conn.commit()

	def db_init(self):

		cur.executescript('''
			CREATE TABLE IF NOT EXISTS Users(
				id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
				name TEXT UNIQUE,
				token_id INTERGER,
				user_id TEXT UNIQUE
			);

			CREATE TABLE IF NOT EXISTS Tokens(
				id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
				token TEXT,
				secret TEXT
			);

			CREATE TABLE IF NOT EXISTS Albums(
				id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
				title TEXT,
				description TEXT,
				photoset_id TEXT UNIQUE,
				user_id INTEGER
			);

			CREATE TABLE IF NOT EXISTS Photos(
				id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
				title TEXT,
				description TEXT,
				album_id TEXT,
				photo_id TEXT UNIQUE,
				link TEXT UNIQUE
			);
		''')

	def get_usertokens(self):
		return self.tokens

	def get_appkeys(self):
		return self.keys

	def get_userid(self):
		return self.user_id

class photosets(object):

	def __init__(self, tokens, nojsoncallback=True, format='json', parameters=None):

		self.keys = hidden.keys()
		self.dbtokens = tokens

		self.dbtokens["token"].encode("ascii")
		self.dbtokens["token_secret"].encode('ascii')

		if self.dbtokens is not None:

			self.consumer = oauth.OAuthConsumer(self.keys["oauth_consumer_key"], self.keys["oauth_consumer_secret"])
			self.token = oauth.OAuthToken(self.dbtokens["token"].encode("ascii"), self.dbtokens["token_secret"].encode("ascii"))

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
			#print defaults
			self.parameters = defaults

		else:
			print "token is none"

	def make_request(self,parameter=None):

		req = oauth.OAuthRequest(http_method="GET", http_url=self.url, parameters=parameter)
		req.sign_request(oauth.OAuthSignatureMethod_HMAC_SHA1(),self.consumer, self.token)

		url = req.to_url()
		return url

	# page and per_page set default to None to get the whole photoset list
	def photosetList_byUserid(self, user_id, page = None, per_page = None):

		self.user_id = user_id

		params = self.parameters.copy()
		params.update({
			"method": "flickr.photosets.getList",
			"user_id": user_id,
			"page": page,
			"per_page": per_page
		})

		url = self.make_request(params)

		print "Getting photoset lists......"
		print
		data = urllib.urlopen(url).read()

		js = json.loads(data)

		if js["stat"] == "fail":
			print "Fail Code: ", js["code"], " Message: ", js["message"]
		elif js["stat"] == "ok":	#Successful
			print "Successfully getting photoset list!"
			print

			cur.execute('''SELECT id FROM Users WHERE user_id = ?''',(user_id, ) )
			uid = cur.fetchone()[0]

			for item in js["photosets"]["photoset"]:

				photoset_id = item["id"]
				title = item["title"]["_content"]
				description = item["description"]["_content"]

				cur.execute('''
					INSERT OR IGNORE INTO Albums (title, description, user_id, photoset_id)
					VALUES (?, ?, ?, ?)''', ( title, description, uid, photoset_id ) )

			conn.commit()

	def photoList_bySetid(self, user_id, set_id):

		params = self.parameters.copy()

		params.update({
			"method": "flickr.photosets.getPhotos",
			"user_id": user_id,
			"photoset_id": set_id
		})

		url = self.make_request(params)

		data = urllib.urlopen(url).read()
		js = json.loads(data)

		if js["stat"] == "fail":
			print "Fail Code: ", js["code"], " Message: ", js["message"]
		elif js["stat"] == "ok":	#Successful

			for item in js["photoset"]["photo"]:

				title = item["title"]
				photo_id = item["id"]

				cur.execute('''
					INSERT OR IGNORE INTO Photos (title, album_id, photo_id)
					VALUES (?, ?, ?)''', ( title, set_id, photo_id ) )

				conn.commit()

				# Get photo infos for current photo
				self.getInfo_byPhotoID(photo_id)

	def getSize_byPhotoid(self, photo_id, size=0):

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
			print "Get photo url in size ", size, "fail."
		elif js["stat"] == "ok":
			print "Got photo url in size ", size, "......"

			for item in js["sizes"]["size"]:
				if int(item["width"]) == size and size != 0:
					src = item["source"]
					#print src

			cur.execute('''
				UPDATE Photos SET link = ? WHERE photo_id = ?''', (src, photo_id ) )
			conn.commit()
		return src

	def getInfo_byPhotoID(self, photo_id):

		params = self.parameters.copy()

		# Update request variables
		params.update({
			"method": "flickr.photos.getInfo",
			"photo_id": str(photo_id)
		})

		# Request call
		url = self.make_request(params)
		data = urllib.urlopen(url).read()
		js = json.loads(data)

		# Handle fail situation
		if js["stat"] == "fail":
			print "Get photo infos fail."
		elif js["stat"] == "ok":
			print "Got photo infos successfully!"

			description = js["photo"]['description']['_content']

			cur.execute('''
				UPDATE Photos SET description = ? WHERE photo_id = ?''', (description, photo_id ) )
			conn.commit()

	def return_photosetList(self):

		cur.execute('''SELECT id FROM Users WHERE user_id = ?''',(self.user_id, ) )
		uid = cur.fetchone()[0]
		print "User in database, id = ", uid

		cur.execute('''SELECT * FROM Albums WHERE user_id = ?''',(uid, ) )

		result = list()

		for item in cur.fetchall():
			result.append({
				"title": item[1],
				"description": item[2],
				"id": item[3]
			})
		return result

	def return_photoList(self, photoset_id):

		result = dict()

		cur.execute('''SELECT title, description FROM Albums WHERE photoset_id = ?''',(photoset_id, ) )
		# Need to consider the possibilities about non-exist photoset_id
		for item in cur.fetchall():
			result["album_name"] = item[0]
			result['album_caption'] = item[1]

		result["photos"] = list()

		cur.execute('''SELECT title, description, photo_id FROM Photos WHERE album_id = ?''', (photoset_id, ) )

		for item in cur.fetchall():

			result["photos"].append({
				"title": item[0],
				"description": item[1],
				"photo_id": item[2]
			})

		return result

import flickr

request_token_url = "http://www.flickr.com/services/oauth/request_token"
api_url = "https://api.flickr.com/services/rest/?"

#user_info = flickrURL.get_user(request_token_url)
#print user_info

fk = flickr.flickrAPI()
fk.get_Tokens(request_token_url)

fk.get_info()
#fk.set_Method()
#fk.flickr_call()
import flickrURL

request_token_url = "http://www.flickr.com/services/oauth/request_token"
api_url = "https://api.flickr.com/services/rest/?"

user_info = flickrURL.get_user(request_token_url)
print user_info

flickrURL.get_Photosets_list(api_url, user_info)
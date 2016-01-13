from flickrURL import get_user

request_token_url = "http://www.flickr.com/services/oauth/request_token"

user_info = get_user(request_token_url)
print user_info
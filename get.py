import flickr

request_token_url = "http://www.flickr.com/services/oauth/request_token"
api_url = "https://api.flickr.com/services/rest/?"

getflickr = flickr.photosets()

url = getflickr.getSizes(23608652504,800)
print url

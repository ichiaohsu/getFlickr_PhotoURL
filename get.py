import flickr
#user_id = 11976680@N00

request_token_url = "http://www.flickr.com/services/oauth/request_token"
api_url = "https://api.flickr.com/services/rest/?"

getflickr = flickr.photosets()

#fk = flickr.flickrInit()
#fk.get_Tokens(request_token_url)
#user_id = raw_input("Enter user id - ")

url = getflickr.getSizes(23608652504,800)
print url

#getflickr.get_setID(user_id)
import flickr
user_id = "11976680@N00"

request_token_url = "http://www.flickr.com/services/oauth/request_token"
api_url = "https://api.flickr.com/services/rest/?"

getflickr = flickr.photosets()

#fk = flickr.flickrInit()
#fk.get_Tokens(request_token_url)
#user_id = raw_input("Enter user id - ")

#url = getflickr.get_photoSize_URL_photoid(23608652504,800)
#print url

photolist = getflickr.get_photoset_List(user_id,1,2)
print "id:", photolist[0]["id"]

polin = getflickr.get_photolist_from_setid(user_id,photolist[0]["id"])
print polin
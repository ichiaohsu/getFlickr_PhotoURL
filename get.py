import flickr

request_token_url = "http://www.flickr.com/services/oauth/request_token"
api_url = "https://api.flickr.com/services/rest/?"

getflickr = flickr.photosets()

#fk = flickr.flickrInit()
#fk.get_Tokens(request_token_url)
user_id = raw_input("Enter user id - ")

#url = getflickr.get_photoSize_URL_photoid(23608652504,800)
#print url

photoset_list = getflickr.get_photoset_List(user_id,1,2)

photo_list = getflickr.get_photolist_from_setid(user_id,photoset_list[0]["id"])

print photo_list

for i in photo_list["photo"]:
	src = getflickr.get_photoSize_URL_photoid(i["id"], 800)
	i["src"] = src

print photo_list
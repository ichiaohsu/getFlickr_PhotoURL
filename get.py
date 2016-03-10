import flickr
import json

#getflickr = flickr.photosets()

user_name = raw_input("Enter user name - ")

login = flickr.login(user_name)

token = login.get_usertokens()
keys = login.get_appkeys()
#print token
#print token["token"],token["token_secret"]
#print keys["oauth_consumer_key"],keys["oauth_consumer_secret"]

# Get user_id from login object
user_id = login.get_userid()
print user_id
print

photoset = flickr.photosets(token, True, 'json', None)
photoset_list = photoset.get_photoset_List(user_id)

print photoset_list
print 

photo_list = photoset.get_photolist_from_setid(user_id, photoset_list[0]["id"])

print photo_list
print

for i in photo_list["photo"]:
	src = photoset.get_photoSize_URL_photoid(i["id"], 800)
	print "src: ", src
	i["src"] = src

fp = open("Album.js","w")
json.dump(photo_list, fp, indent=4)

fp.close()

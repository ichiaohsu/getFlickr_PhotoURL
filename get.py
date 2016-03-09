import flickr
import json

#getflickr = flickr.photosets()

user_name = raw_input("Enter user name - ")

login = flickr.login(user_name)

token = login.get_usertokens()
keys = login.get_appkeys()
print token["token"],token["token_secret"]
print keys["oauth_consumer_key"],keys["oauth_consumer_secret"]


photoset_list = flickr.photosets(token, True, 'json', None)
photo_list = photoset_list.get_photoset_List()

print photo_list

"""
print photo_list

for i in photo_list["photo"]:
	src = getflickr.get_photoSize_URL_photoid(i["id"], 800)
	print "src: ", src
	i["src"] = src

print photo_list

fp = open("Album.js","w")
json.dump(photo_list, fp, indent=4)

fp.close()
"""
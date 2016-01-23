import flickr
import json

getflickr = flickr.photosets()

#fk = flickr.flickrInit()
#fk.get_Tokens()

user_id = raw_input("Enter user id - ")

photoset_list = getflickr.get_photoset_List(user_id,1,2)

photo_list = getflickr.get_photolist_from_setid(user_id,photoset_list[1]["id"])

print photo_list

for i in photo_list["photo"]:
	src = getflickr.get_photoSize_URL_photoid(i["id"], 800)
	print "src: ", src
	i["src"] = src

print photo_list

fp = open("Album.js","w")
json.dump(photo_list, fp, indent=4)

fp.close()
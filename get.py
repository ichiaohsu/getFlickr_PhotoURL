import flickr
import json

user_name = raw_input("Enter user name - ")

login = flickr.login(user_name)

token = login.get_usertokens()
keys = login.get_appkeys()

# Get user_id from login object
user_id = login.get_userid()
print "User id: ", user_id
print

photoset = flickr.photosets(token, True, 'json', None)
#photoset_list = photoset.get_photoset_List(user_id)
photoset.photosetList_byUserid(user_id)

photoset_list = photoset.return_photosetList()

#print photoset_list
#print len(photoset_list)

def print_title(argument):

	for i in argument:
		print i["title"]
	print

print_title(photoset_list)

"""
while True:
		
	for item in photo_list:
		print item["title"]
	user_selection = raw_input("Please selct a photoset - ")
"""

photoset.photoList_bySetid(user_id, photoset_list[1]["id"])
photo_list = photoset.return_photoList(photoset_list[1]["id"])


print_title(photo_list["photo"])
#print photo_list
#print

for i in photo_list["photo"]:
	src = photoset.getSize_byPhotoid(i["photo_id"],800)
	#src = photoset.get_photoSize_URL_photoid(i["id"], 800)

	print "src: ", src
	#i["src"] = src
"""
fp = open("Album.js","w")
json.dump(photo_list, fp, indent=4)

fp.close()
"""
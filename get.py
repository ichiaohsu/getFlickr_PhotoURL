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

set_obj = flickr.photosets(token, True, 'json', None)
#photoset_list = photoset.get_photoset_List(user_id)
set_obj.photosetList_byUserid(user_id)

photoset_list = set_obj.return_photosetList()

#print photoset_list
#print len(photoset_list)

def print_title(argument):
	print
	for i in argument:
		print i["title"]
	print

print_title(photoset_list)

def getAllPhotos():

	print "Getting All photos from your flickr. Please wait......"
	print
	for album in photoset_list:
		print "Processing getting photos from album: ", album['title'], ' ......'
		print
		# Store photos in database
		set_obj.photoList_bySetid(user_id, album['id'])

#getAllPhotos()

def showSelector(album_list):

	count = 1
	for i in album_list:
		print str(count), '.' , i['title']
		count = count + 1

	selected = raw_input("Enter the number of albums you want to get and Seperate with comma. Ex: 1,2,5 - ")
	select_list = selected.split(',')
	select_albumid = list()

	for index in select_list:
		select_albumid.append(album_list[int(index)-1]['id'])
		print "Select ", album_list[int(index)-1]['title']
	return select_albumid

chosen_albumid = showSelector(photoset_list)
print chosen_albumid

def getChosenPhotos(album_id):
	albums = list()
	#photo_list = list()
	for index, val in enumerate(album_id):
		albums.append( set_obj.return_photoList(val) )
		#print albums
		#print

		for p in albums[index]['photos']:
			p['src'] = set_obj.getSize_byPhotoid(p['photo_id'],800)
		#for p in photos:
		#	p['src'] = set_obj.getSize_byPhotoid(p['photo_id'],800)

	return albums
#photoset.photoList_bySetid(user_id, photoset_list[0]["id"])
#photo_list = photoset.return_photoList(photoset_list[0]["id"])

chosen_album = getChosenPhotos(chosen_albumid)
print chosen_album
#print_title(photo_list["photo"])
#print photo_list
#print

'''
for i in photo_list["photo"]:
	src = set_obj.getSize_byPhotoid(i["photo_id"],800)
	#src = set_obj.get_photoSize_URL_photoid(i["id"], 800)

	print "src: ", src
	#i["src"] = src
'''

def writeJSON(argument):
	fp = open("Album.js","w")
	json.dump(argument, fp, indent=4)

	fp.close()

#writeJSON(photo_list)

def formatDict(arg):
	format_final = {
		'albums': arg
	}
	writeJSON(format_final)

formatDict(chosen_album)

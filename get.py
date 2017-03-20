import flickr
import json

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

def prepareChosenPhotos(arg):

	print
	print "Getting All chosen photos from your flickr. Please wait......"
	print
	for album in arg:

		print "......"
		# Store photos in database
		set_obj.photoList_bySetid(user_id, album)

def getChosenPhotoLink(album_id):
	
	albums = list()
	for index, val in enumerate(album_id):
		albums.append( set_obj.return_photoList(val) )

		print "Getting photo from album ", albums[index]['album_name'], '......'
		for p in albums[index]['photos']:

			p['src'] = set_obj.getSize_byPhotoid(p['photo_id'],800)
			del p['photo_id']

	return albums

def writeJSON(argument):

	print
	save_name = raw_input("Enter desired file name - ") + ".js"
	print

	fp = open(save_name,"w")
	json.dump(argument, fp, indent=4)

	fp.close()

def formatDict(arg):
	format_final = {
		'albums': arg
	}
	writeJSON(format_final)

if __name__ == '__main__':

	user_name = raw_input("Enter user name - ")

	login = flickr.login(user_name)

	token = login.get_usertokens()
	keys = login.get_appkeys()

	# Get user_id from login object
	user_id = login.get_userid()
	print "login User: ", user_name, " id: ", user_id
	print

	# Initialization of a photoset object
	set_obj = flickr.photosets(token, True, 'json', None)

	# Get all photosets under the same author
	set_obj.photosetList_byUserid(user_id)

	photoset_list = set_obj.return_photosetList()

	# Show selector to users and get list of chosen albums
	chosen_albumid = showSelector(photoset_list)

	# Prepare all photo info needed in advance
	prepareChosenPhotos(chosen_albumid)

	# Request direct link from flickr for each photos
	chosen_album = getChosenPhotoLink(chosen_albumid)

	# Save JSON
	formatDict(chosen_album)

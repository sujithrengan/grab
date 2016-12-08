from mutagen.mp4 import MP4,MP4Cover
import grabberutils as utils
import requests
class track:
	def __init__(self):
		self.name=''
		self.album=''
		self.artist=''
		self.album_artist=''
		self.year=''
		self.copyright=''
		self.album_art=''
		self.lyric=''
		self.genre=''
		self.track_number=1
		self.total_tracks=1
		self.url=''
		self.duration_ms=0
		self.fname=''

	def print_info(self):
		print("name: "+self.name)
		print("album: "+self.album)
		print("artist: "+self.artist)
		print("year: "+self.year)
		print("album_art: "+self.album_art)
		print("track_number: "+str(self.track_number))
		print("url: "+self.url)
		print("duration_ms: "+str(self.duration_ms))


class tagtask:

	def __init__(self,strack):
		self.songtrack=strack

	def prog_print(self,text,status=0):
		if status==0:
			print('['+self.songtrack.name+'] '+text)
		elif status==1:
			print(utils.highlight.OKGREEN+'['+self.songtrack.name+'] '+text+utils.highlight.ENDC)
		elif status==-1:
			print(utils.highlight.FAIL+'['+self.songtrack.name+'] '+text+utils.highlight.ENDC)



	def tag_now(self):
		self.tag_text()
		self.tag_image(0)
	
	def tag_text(self):
		trackfile=MP4(self.songtrack.fname+'.m4a')
		trackfile['\xa9alb']=self.songtrack.album
		trackfile['\xa9ART']=self.songtrack.artist
		trackfile['\xa9nam']=self.songtrack.name
		trackfile['aART']=self.songtrack.album_artist
		trackfile['\xa9day']=self.songtrack.year
		trackfile['\xa9gen']=self.songtrack.genre
		trackfile['\xa9lyr']=self.songtrack.lyric
		trackfile['cprt']=self.songtrack.copyright
		trackfile['trkn']=[[self.songtrack.track_number,self.songtrack.total_tracks]]
		trackfile.save()
		self.prog_print('Fixed. Adding Art...')

	def tag_image(self,attempt):
		if(attempt>utils.backoff_threshold):
			print('Giving up.')
			return

		try:
			trackfile=MP4(self.songtrack.fname+'.m4a')
			art=requests.get(self.songtrack.album_art,timeout=10)
			trackfile['covr']=[MP4Cover(art.content,MP4Cover.FORMAT_JPEG)]
			trackfile.save()
			self.prog_print('Art Added. All Done.',1)
		except requests.exceptions.Timeout:
			print('TimedOut. Retrying in 5 seconds...')
			sleep(5)
			self.tag_image(attempt+1)
		except KeyboardInterrupt:
			sys.exit('\nExiting...')
		except:
			print('Skipping AlbumArt...All Done.')

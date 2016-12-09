from __future__ import unicode_literals
import requests,youtube_dl,sys,json,os
from bs4 import BeautifulSoup
from time import sleep
import grabberutils as utils
import tagger

class grabtask:

	def __init__(self):
		self.songtrack=tagger.track()

	def prog_print(self,text,status=0):
		if status==0:
			print('['+self.songtrack.name+'] '+text)
		elif status==1:
			print(utils.highlight.OKGREEN+'['+self.songtrack.name+'] '+text+utils.highlight.ENDC)
		elif status==-1:
			print(utils.highlight.FAIL+'['+self.songtrack.name+'] '+text+utils.highlight.ENDC)

	def search_lyric_mx(self,attempt):
		if(attempt>utils.backoff_threshold):
			print('Giving up.')
			return

		query=self.songtrack.name+' '+self.songtrack.artist
		req_url=utils.base_m_lyric_search.replace('PH_QUERY',query)
		req_url=req_url.replace(' ','%20')
		req_headers = {'User-Agent': 'grab'}
		
		try:
			response=requests.get(req_url,headers=req_headers,timeout=5)
			soup=BeautifulSoup(response.text,'html.parser')
			best_track=soup.find_all('a',attrs={'class': 'title'})[0].get('href')
			
			req_url=utils.base_m_lyric_info.replace('PH_TRACK',best_track)

			response=requests.get(req_url,headers=req_headers,timeout=5)
			soup=BeautifulSoup(response.text,'html.parser')
			lyr=''
			#lyr_tags=soup.find_all('p',attrs={'class':'mxm-lyrics__content'})
			lyr_tags=soup.find_all('script')
			for i in range(0,len(lyr_tags)):
				if('var __mxmProps' in lyr_tags[i].text):
					forced_info=lyr_tags[i].text[lyr_tags[i].text.find('var __mxmState')+len('var __mxmState= ')+1:-1]
					data=json.loads(forced_info)
					if(data['page']['track']['hasLyrics']==1):
						self.songtrack.lyric=data['page']['lyrics']['lyrics']['body']
					else:
						self.prog_print('Lyrics not found. Skipping...')

					break

		except Exception as e:
			self.prog_print('Lyrics not found. Skipping...')


	def fix_track(self):
		tagger.tagtask(self.songtrack).tag_now()

	def clean_up_dir(self):
		try:
			os.remove('./'+self.songtrack.fname+'.m4a.part')
			os.remove('./'+self.songtrack.fname+'.m4a.part-Frag0.part')
			os.remove('./.simulate.info.json')
		except Exception as e:
			pass

	def grab_track_yt(self,attempt,query):

		def yt_progress(progress):
			#print(progress)
			if(progress['status']=='error'):
				print('Error Downloading.')

			elif(progress['status']=='downloading'):
				down=progress['downloaded_bytes']
				try:
					total=progress['total_bytes']
				
				except:
					try:
						total=progress['total_bytes_estimate']
					except:
						total=4000000

				count=int(50*down/total)
				sys.stdout.write('\r')
				sys.stdout.write("%-10s[%-50s] %d%%" % (str(int(progress['speed']/1000))+'KB/s','#'*count, count*2))
				sys.stdout.flush()

			elif(progress['status']=='finished'):
				print('\n')
				self.prog_print('Track Downloaded. Fixing...')

		
		#print(query)
		self.songtrack.fname=self.songtrack.name+' - '+self.songtrack.album_artist
		
		ydl_opts_simulate={'quiet':1,'no_warnings':1,'format':'140', \
					'outtmpl':'.simulate',\
					'writeinfojson':1,'skip_download':1,}
		ydl_opts={'quiet':1,'no_warnings':1,'format':'140', \
					'outtmpl':self.songtrack.fname+'.%(ext)s',\
					'progress_hooks': [yt_progress],}
		ydl_simulate=youtube_dl.YoutubeDL(ydl_opts_simulate)
		ydl=youtube_dl.YoutubeDL(ydl_opts)

		try:
			dl=False
			for i in range(1,utils.range_threshold+1):
				ydl_simulate.download(['gvsearch'+str(i)+':youtube:'+query+' '*(i-1)])
				with open('.simulate.info.json') as data_file:
					data = json.load(data_file)
					#print(data['fulltitle'])
					#print(data['uploader'])
					#print(data['webpage_url'])
					if abs(self.songtrack.duration_ms-data['duration']*1000)<utils.duration_threshold:
						ydl.download([data['webpage_url']])
						data_file.close()
						
						try:		
							os.remove('./.simulate.info.json')
						except OSError as e:
							print(e.strerror)
						
						if os.path.isfile(self.songtrack.fname+'.m4a'):
							dl=True
							break

			if dl:
				self.search_lyric_mx(0)
				self.fix_track()
			else:
				if attempt==0 and utils.quick_mode==False:
					print(utils.highlight.WARN+'Couldn\'t find track. Searching alternatives...'+utils.highlight.ENDC)
					self.grab_track_yt(attempt+1,query+' audio')
				else:
					print(utils.highlight.FAIL+'Download failed.'+utils.highlight.ENDC)
		
		except Exception as e:			
			self.clean_up_dir()
			print(utils.highlight.FAIL+'Download failed.'+utils.highlight.ENDC)	

		except KeyboardInterrupt:
			self.clean_up_dir()
			sys.exit('\nExiting...')
		

	def extract_track_spotify(self,tracks,index):
		self.songtrack.name=tracks['tracks']['items'][index]['name']
		self.songtrack.artist=tracks['tracks']['items'][index]['artists'][0]['name']
		self.songtrack.track_number=tracks['tracks']['items'][index]['track_number']
		self.songtrack.duration_ms=tracks['tracks']['items'][index]['duration_ms']
		self.songtrack.album=tracks['tracks']['items'][index]['album']['name']
		self.songtrack.album_artist=tracks['tracks']['items'][index]['album']['artists'][0]['name']
		self.songtrack.album_art=tracks['tracks']['items'][index]['album']['images'][0]['url']
		self.songtrack.total_tracks, \
		self.songtrack.year,	\
		self.songtrack.copyright= self.extract_album_info_spotify(\
								tracks['tracks']['items'][index]['album']['id'])


	def extract_track_itunes(self,tracks,index):
		self.songtrack.name=tracks['results'][index]['trackName']
		self.songtrack.artist=tracks['results'][index]['artistName']
		self.songtrack.track_number=tracks['results'][index]['trackNumber']
		self.songtrack.duration_ms=tracks['results'][index]['trackTimeMillis']
		self.songtrack.album=tracks['results'][index]['collectionName']
		try:
			self.songtrack.album_artist=tracks['results'][index]['collectionArtistName']
		except:
			self.songtrack.album_artist=self.songtrack.artist

		self.songtrack.album_art=tracks['results'][index]['artworkUrl100']\
								.replace('100x100bb','600x600bb')
		self.songtrack.total_tracks=tracks['results'][index]['trackCount']
		self.songtrack.year=tracks['results'][index]['releaseDate']
		self.songtrack.copyright= '_iTunes_'
		self.songtrack.genre=tracks['results'][index]['primaryGenreName']
	

	def extract_album_info_spotify(self,arg_album):

		req_url=utils.base_s_album_info.replace('PH_ALBUM',arg_album)
		req_url=req_url.replace(' ','%20')

		try:
			response=response=requests.get(req_url,timeout=5)
			album=response.json()
			label=''
			try:
				label=album['label']
			except:
				pass

			return (album['tracks']['total'] , album['release_date'].split('-')[0] ,\
					label)

		except:
			pass

	def search_track_spotify_interactive(self,attempt,arg_track):
		
		if(attempt>utils.backoff_threshold):
			print('Giving up.')
			return

		req_url=utils.base_s_track_search_interactive.replace('PH_QUERY',arg_track)
		req_url=req_url.replace(' ','%20')
		
		try:
			response=requests.get(req_url,timeout=5)
			tracks=response.json()

			if tracks['tracks']['total']==0:
				print(utils.highlight.FAIL+'Track not found. Try altering your search.'+utils.highlight.ENDC)

			
			for index in range(0,tracks['tracks']['total']):
				sys.stdout.write('\r')
				sys.stdout.write(tracks['tracks']['items'][index]['name']+'(' + \
								tracks['tracks']['items'][index]['album']['name'] + \
								') by ' + tracks['tracks']['items'][index]['album']['artists'][0]['name'])
				sys.stdout.flush()
				inp=raw_input('	Download this? (y/n)')

				if(str(inp)=='y'):
					self.extract_track_spotify(tracks,index)
					self.prog_print('Track found. Setting up download...')
					query=self.songtrack.name+' '+self.songtrack.album_artist
					self.grab_track_yt(0,query)
					break
				else:
					pass

		except requests.exceptions.Timeout:
			print('Connection timeout. Retrying in 5 seconds...')
			sleep(5)
			self.search_track_spotify_ineractive(attempt+1)
		except requests.exceptions.ConnectionError:
			print('Network Error. Please check connection and try again.')
		except IndexError,KeyError:
			print(utils.highlight.FAIL+'Track not found. Try altering your search.'+utils.highlight.ENDC)
		except KeyboardInterrupt:
			sys.exit('\nExiting...')


	def search_track_itunes_interactive(self,attempt,arg_track):
		
		if(attempt>utils.backoff_threshold):
			print('Giving up.')
			return

		req_url=utils.base_i_track_search.replace('PH_TRACK',arg_track)
		req_url=req_url.replace(' ','+')
		
		try:
			response=requests.get(req_url,timeout=5)
			tracks=response.json()

			if tracks['resultCount']==0:
				print(utils.highlight.FAIL+'Track not found. Try altering your search.'+utils.highlight.ENDC)

			for index in range(0,tracks['resultCount']):
				sys.stdout.write('\r')
				sys.stdout.write(tracks['results'][index]['trackName']+'(' + \
								tracks['results'][index]['collectionName'] + \
								') by ' + tracks['results'][index]['artistName'])
				sys.stdout.flush()
				inp=raw_input('	Download this? (y/n)')

				if(str(inp)=='y'):
					self.extract_track_itunes(tracks,index)
					self.prog_print('Track found. Setting up download...')
					query=self.songtrack.name+' '+self.songtrack.album_artist
					self.grab_track_yt(0,query)
					break
				else:
					pass

		except requests.exceptions.Timeout:
			print('Connection timeout. Retrying in 5 seconds...')
			sleep(5)
			self.search_track_itunes_ineractive(attempt+1)
		except requests.exceptions.ConnectionError:
			print('Network Error. Please check connection and try again.')
		except IndexError,KeyError:
			print(utils.highlight.FAIL+'Track not found. Try altering your search.'+utils.highlight.ENDC)
		except KeyboardInterrupt:
			sys.exit('\nExiting...')



	def search_track_spotify(self,attempt,arg_track,arg_artist):
		'''
		Searches the track specified withe the artist on spotify.
		If result empty, forwards to a plain search without the artist

		'''
		if(attempt>utils.backoff_threshold):
			print('Giving up.')
			return

		
		req_url=utils.base_s_track_search.replace('PH_TRACK',arg_track)
		req_url=req_url.replace('PH_ARTIST',arg_artist)
		req_url=req_url.replace(' ','%20')
		#print(req_url)
		try:
			response=requests.get(req_url,timeout=5)
			self.extract_track_spotify(response.json(),0)
			self.prog_print('Track found. Setting up download...')

			#self.songtrack.print_info()
			query=self.songtrack.name+' '+self.songtrack.album_artist
			self.grab_track_yt(0,query)
			#self.search_track_lastfm()

		except requests.exceptions.Timeout:
			print('Connection timeout. Retrying in 5 seconds...')
			sleep(5)
			self.search_track_spotify(attempt+1)
		except requests.exceptions.ConnectionError:
			print('Network Error. Please check connection and try again.')
		except IndexError,KeyError:
			print(utils.highlight.WARN+'Track not found. Bringing up sugestions...'+utils.highlight.ENDC)
			self.search_track_spotify_interactive(0,arg_track)
		except KeyboardInterrupt:
			sys.exit('\nExiting...')


	def search_track_itunes(self,attempt,arg_track,arg_artist):
		'''
		Searches the track specified withe the artist on itunes.
		If result empty, forwards to a plain search without the artist

		'''
		if(attempt>utils.backoff_threshold):
			print('Giving up.')
			return

		
		req_url=utils.base_i_track_search.replace('PH_TRACK',arg_track+'+'+arg_artist)
		req_url=req_url.replace(' ','+')
		#print(req_url)
		try:
			response=requests.get(req_url,timeout=5)
			self.extract_track_itunes(response.json(),0)
			self.prog_print('Track found. Setting up download...')

			#self.songtrack.print_info()
			query=self.songtrack.name+' '+self.songtrack.album_artist
			self.grab_track_yt(0,query)
			#self.search_track_lastfm()

		except requests.exceptions.Timeout:
			print('Connection timeout. Retrying in 5 seconds...')
			sleep(5)
			self.search_track_itunes(attempt+1)
		except requests.exceptions.ConnectionError:
			print('Network Error. Please check connection and try again.')
		except IndexError,KeyError:
			print(utils.highlight.WARN+'Track not found. Bringing up sugestions...'+utils.highlight.ENDC)
			self.search_track_itunes_interactive(0,arg_track)
		except KeyboardInterrupt:
			sys.exit('\nExiting...')


	
def grab_now(args):
	'''
	Parsing all the arguments and validating for confilicting modes. 
	Call to respective modes.

	'''

	if args.error!=None:
		utils.duration_threshold=args.error*1000
	if args.quick==True:
		utils.quick_mode=True
	if args.itunes==True:
		utils.source=1;

	if args.file!=None:
		
		try:
			with open(args.file) as file:
				file_input=str(file.read()).split('\n')
				for i in range(file_input.index('@@begin_tracks')+1,file_input.index('@@end_tracks')):
					if(file_input[i][0:2]!='##' and file_input[i].strip()!=''):
						query_line=file_input[i].split('//')
						if len(query_line)==1:
							grabtask().search_track_spotify_interactive(0,query_line[0])
						else:
							grabtask().search_track_spotify(0,query_line[0],query_line[1])



		except IOError as e:
			print('File not found. File generated. Edit file as needed and try again.')
			with open(args.file,'w') as file:
				file.write(utils.file_mode_template)
		except Exception:
			sys.exit('File template mismatch')	


	elif args.artist==None:
		
		if args.track!=None:

			if utils.source==0:
				args.artist=''
				print(utils.highlight.WARN+'Artist not specified. Bringing up sugestions...'+utils.highlight.ENDC)
				grabtask().search_track_spotify_interactive(0,args.track)
			else:
				args.artist=''
				print(utils.highlight.WARN+'Artist not specified. Bringing up sugestions...'+utils.highlight.ENDC)
				grabtask().search_track_itunes_interactive(0,args.track)
			
		elif args.album!=None:
			pass
		
		else:	
			sys.exit('Album or track missing')
		
	elif args.album!=None:
		
		pass

	elif args.track!=None:
		#print('To download: ' + self.args.artist)
		print('Identifying Track...')
		if utils.source==0:
			grabtask().search_track_spotify(0,args.track,args.artist)

		else:
			grabtask().search_track_itunes(0,args.track,args.artist)

	
	else:
		sys.exit('Album or track missing')
	


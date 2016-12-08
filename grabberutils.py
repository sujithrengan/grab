
api_key='f8abe4f577f9bbc882861a2674ecf3ba'

base_l_track_search='http://ws.audioscrobbler.com/2.0/?method=track.search&track=PH_TRACK&api_key=PH_API_KEY&format=json'
base_l_album_search='http://ws.audioscrobbler.com/2.0/?method=album.search&album=PH_ALBUM&api_key=PH_API_KEY&format=json'
base_l_track_info='http://ws.audioscrobbler.com/2.0/?method=track.getInfo&api_key=PH_API_KEY&artist=PH_ARTIST&track=PH_TRACK&format=json'
base_l_album_info='http://ws.audioscrobbler.com/2.0/?method=album.getinfo&api_key=PH_API_KEY&artist=PH_ARTIST&album=PH_ALBUM&format=json'

base_s_track_search='https://api.spotify.com/v1/search?q=track:PH_TRACK%20artist:PH_ARTIST&type=track'
base_s_track_search_interactive='https://api.spotify.com/v1/search?q=PH_QUERY&type=track'
base_m_lyric_search='https://www.musixmatch.com/search/PH_QUERY'
base_m_lyric_info='https://www.musixmatch.comPH_TRACK'

backoff_threshold=3
duration_threshold=3000
range_threshold=3
file_mode_template ='##Modify this file as needed.\n##Lines starting with \'##\' are ignored.' + \
					 '\n##Do not modify lines starting with \'@@\'.\n\n@@begin_tracks\n##List'+ \
					 ' tracks below as <trackname>//<artist> or just <trackname>\n##Examples:'+ \
					 '\n##don\'t let me down//chainsmokers\n##High Hopes\n\n\n\n\n@@end_tracks'+\
					 '\n\n@@begin_albums\n##List'+ \
					 ' albums below as <albumname>//<artist> or just <albumname>\n##Examples:'+ \
					 '\n##Bangerz//miley cyrus\n##Pure Heroine\n\n\n\n\n@@end_album'

class highlight:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARN = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

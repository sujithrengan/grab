import argparse,sys
import grabber

def script():
	parser=argparse.ArgumentParser(description='Grab any track or album,\
									 with original metadata and abum art.')
	group_mode=parser.add_mutually_exclusive_group()
	group_source=parser.add_mutually_exclusive_group()
	
	parser.add_argument('-a','--artist',help="Artist of the track/album.",type=str)
	parser.add_argument('-e','--error',help="Error tolerance (1-9) (1 for very strict,\
	 					9 for otherwise)",type=int)
	parser.add_argument('-q','--quick',help="Limited search space.",\
						action="store_true")
	
	group_mode.add_argument('-A','--album',help="Album to download",type=str)
	group_mode.add_argument('-t','--track',help="Track to download",type=str)
	group_mode.add_argument('-f','--file',help="Download tracks/abums listed in the file.Use the same"+\
						" a template of the same name.")

	group_source.add_argument('-i','--itunes',help="Search from iTunes",action="store_true")
	group_source.add_argument('-s','--spotify',help="Search from Spotify (Default)",\
							action="store_true")


	args=parser.parse_args()


	grabber.grab_now(args)


if __name__== '__main__':
	sys.exit(script())
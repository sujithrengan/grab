# grab
Search and download any tack or album with original metadata.

##Requirements
Requires Python 2

##Installation
Clone the repo or download zip.
`cd` into the cloned folder and:

`pip install -r requires`

##Usage

`python grab.py [-h] [-a ARTIST] [-e ERROR] [-q] [-A ALBUM | -t TRACK | -f FILE ]`

##Options

  	-h, --help            		show this help message and exit
  	-a ARTIST, --artist ARTIST	Artist of the track/album
  	-e ERROR, --error ERROR		Error tolerance (1-9) (1 for very strict, 9 for
                        		otherwise)
  	-q, --quick           		Limited search space
  	-A ALBUM, --album ALBUM		Album to download
  	-t TRACK, --track TRACK		Track to download
  	-f FILE, --file FILE  		Download tracks/abums listed in the file. Use the same to
                        		generate a template of the same name and edit as needed.
	-i, --itunes         		Search from iTunes
	-s, --spotify         		Search from Spotify (Default)

##Examples:

* `python grab.py -t "dreamin'" -a 'raelee nikole'`
* `python grab.py -f 'list.txt'`
* `python grab.py -t 'alone' -e 5`


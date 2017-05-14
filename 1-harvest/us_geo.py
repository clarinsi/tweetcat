# you can obtain the four values required below by registering your app at https://apps.twitter.com
CONSUMER_KEY=''
CONSUMER_SECRET=''
ACCESS_TOKEN=''
ACCESS_TOKEN_SECRET=''

BATCH_SIZE=1000 # number of tweets written to disk together in a file

MODE='GEO'
#MODE='LANG'

# define if MODE is GEO, ignore if MODE is LANG
# lower left corner, can be obtained from http://www.latlong.net
MINLAT=22
MINLON=-125
# upper right corner
MAXLAT=50
MAXLON=-66
# language codes of interest, list available from https://github.com/saffsd/langid.py
# will not be used during the collection process, but at its end if filter_users.py is run
LANGID_GEO=[]
# country codes of interest, https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2
# will not be used during the collection process, but at its end if filter_users.py is run
COUNTRIES=['US']

# define if MODE is LANG, ignore if MODE is GEO
SEEDS='seeds.hbs'
LANGID_LANG=['hr','sr','bs'] # language codes of interest, list available from https://github.com/saffsd/langid.py

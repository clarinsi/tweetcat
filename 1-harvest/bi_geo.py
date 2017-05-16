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
MINLAT=50
MINLON=-11
# upper right corner
MAXLAT=60
MAXLON=2
# language codes of interest, list available from https://github.com/saffsd/langid.py
# will not be used during the collection process, but at its end if filter_geo.py is run
LANGID_GEO=[]
# country codes of interest, https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2
# will not be used during the collection process, but at its end if filter_geo.py is run
COUNTRIES=['GB','IE']

# define if MODE is LANG, ignore if MODE is GEO
SEEDS='seeds.hbs'
LANGID_LANG=['hr','sr','bs'] # language codes of interest, list available from https://github.com/saffsd/langid.py

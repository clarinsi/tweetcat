import sys
import tweepy
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from time import sleep,time
from datetime import datetime
from xml.sax.saxutils import escape
from shutil import move,copy
import cPickle as pickle
import re
import os.path
import langid
import json
import gzip

def clean(timeline):
  import re
  stuff=re.compile(r'\bhttp\S+|\b@\w+|\b#\w+',re.UNICODE)
  return ' '.join([' '.join(re.findall(r'\w+',stuff.sub(' ',e.text.lower()),re.UNICODE)) for e in timeline])

def lang_id(timeline):
  timeline=clean(timeline)
  lang=langid.classify(timeline)[0]
  log.write(datetime.now().isoformat()+'\t'+repr(timeline[:200])+' identified as '+lang+'\n')
  return lang in LANGID_LANG

def search(term):
  try:
    result=api.search(term)
  except Exception as e:
    log.write(datetime.now().isoformat()+'\t'+str(e)+'\n')
    log.flush()
    return []
  return result

def followers(user):
  try:
    result=user.followers()
  except:
    return []
  return result

def friends(user):
  try:
    result=user.friends()
  except:
    return []
  return result

def new_user_timeline(screen_name):
  try:
    timeline=[e for e in tweepy.Cursor(api.user_timeline,id=screen_name).items(200)]
  except:
    return None
  if len(timeline)<100:
    log.write(datetime.now().isoformat()+'\tNew user '+screen_name+' did not pass the tweet number threshold ('+str(len(timeline))+') for accurate language identification.\n')
    return False
  if lang_id(timeline):
    timeline=[]
    try:
      for page in tweepy.Cursor(api.user_timeline,id=screen_name,count=200).pages(16):
        timeline.extend(page)
    except:
      log.write(datetime.now().isoformat()+'\tNew user '+screen_name+' did pass the language filter, but could not be retrieved at this point. He will come up again...\n')
      return None
    return sorted(timeline,key=lambda x:x.id)
  else:
    return False

def user_timeline(screen_name,since_id):
  try:
    return sorted(api.user_timeline(screen_name,since_id=since_id),key=lambda x:x.id)
  except:
    return

def write_tweets(tweets,empty=False):
  stop=open(PROJECT+'.busy').read()=='stop'
  if stop and not empty:
    empty=True
  batch_no=0
  while len(tweets)>=BATCH_SIZE or (empty and len(tweets)>0):
    batch_no+=1
    batch=[e._json for e in tweets[:BATCH_SIZE]]
    output=gzip.open(PROJECT+'/'+datetime.now().isoformat()[:10]+'_'+str(batch[0]['id'])+'.gz','w').write(json.dumps(batch,indent=1))
    tweets=tweets[BATCH_SIZE:]
  if batch_no>0:
    log.write(datetime.now().isoformat()+'\tNumber of batches of tweets written: '+str(batch_no)+'\n')
  if stop:
    log.write(datetime.now().isoformat()+'\tStopping with '+str(no_tweets)+' tweets collected.\n')
    serialize()
    sys.exit(0)
  return tweets

def serialize():
  if MODE=='LANG':
    pickle.dump(user_index,open(PROJECT+'.user_index','w'))
    log.write(datetime.now().isoformat()+'\tSerialized the user index\n')

"""
def signal_term_handler(signal,frame):
  log.write(datetime.now().isoformat()+'\tModifying the "busy" file and exiting.\n')
  open(PROJECT+'.busy','w').write('no')
  serialize()
  sys.exit(0)
"""

def lang_mode():
  SLEEP_BETWEEN_ITERATIONS=60*60*12 # number of seconds that should be slept between iterations
  ITERATION_COUNT=0 # 0 for unlimited number of iterations
  global no_tweets
  iterations=0
  tweets=[]
  while True:
    # iterating through seed words and searching for users
    for seed in seedw:
      for hit in search(seed):
        if hit.author.screen_name not in user_index:
          fetched_timeline=new_user_timeline(hit.author.screen_name)
          if fetched_timeline is False:
            log.write(datetime.now().isoformat()+'\tNew user '+hit.author.screen_name+' found by searching did not pass the language filter.\n')
            log.flush()
          elif fetched_timeline is None:
            log.write(datetime.now().isoformat()+'\tNew user '+hit.author.screen_name+' found by searching could not be retrieved. He probably has a protected account.\n')
            log.flush()
          else:
            log.write(datetime.now().isoformat()+'\tFound new user by searching: '+hit.author.screen_name+'\n')
            user_index[hit.author.screen_name]=fetched_timeline[-1].id
            tweets.extend(fetched_timeline)
            no_tweets+=len(fetched_timeline)
            tweets=write_tweets(tweets)
            log.flush()
            for follower in followers(hit.author):
              if follower.screen_name not in user_index:
                fetched_timeline=new_user_timeline(follower.screen_name)
                if fetched_timeline is False:
                  log.write(datetime.now().isoformat()+'\tNew user '+follower.screen_name+' found as follower did not pass the language filter.\n')
                elif fetched_timeline is None:
                  log.write(datetime.now().isoformat()+'\tNew user '+follower.screen_name+' found as follower could not be retrieved. He probably has a protected account.\n')
                else:
                  log.write(datetime.now().isoformat()+'\tFound new user through followers: '+follower.screen_name+'\n')
                  user_index[follower.screen_name]=fetched_timeline[-1].id
                  tweets.extend(fetched_timeline)
                  no_tweets+=len(fetched_timeline)
                  tweets=write_tweets(tweets)
                  log.flush()
            for friend in friends(hit.author):
              if friend.screen_name not in user_index:
                fetched_timeline=new_user_timeline(friend.screen_name)
                if fetched_timeline is False:
                  log.write(datetime.now().isoformat()+'\tNew user '+friend.screen_name+' found as friend did not pass the language filter.\n')
                elif fetched_timeline is None:
                  log.write(datetime.now().isoformat()+'\tNew user '+friend.screen_name+' found as friend could not be retrieved. He probably has a protected account.\n')
                else:
                  log.write(datetime.now().isoformat()+'\tFound new user through friends: '+friend.screen_name+'\n')
                  user_index[friend.screen_name]=fetched_timeline[-1].id
                  tweets.extend(fetched_timeline)
                  no_tweets+=len(fetched_timeline)
                  tweets=write_tweets(tweets)
                  log.flush()
        if open(PROJECT+'.busy').read()=='stop':
          tweets=write_tweets(tweets,True)
          serialize()
          sys.exit(0)
        log.flush()
    # iterating through all known users
    for screen_name,since_id in user_index.items():
      fetched_timeline=user_timeline(screen_name,since_id)
      if fetched_timeline is None:
        log.write(datetime.now().isoformat()+'\tKnown user\'s '+screen_name+' timeline not fetched. Will continue on trying.\n')
        continue
      else:
        if len(fetched_timeline)>0:
          log.write(datetime.now().isoformat()+'\tKnown user\'s '+screen_name+' timeline fetched with '+str(len(fetched_timeline))+' new tweets.\n')
          user_index[screen_name]=fetched_timeline[-1].id
          tweets.extend(fetched_timeline)
          no_tweets+=len(fetched_timeline)
          tweets=write_tweets(tweets)
        else:
          log.write(datetime.now().isoformat()+'\tKnown user\'s '+screen_name+' timeline fetched with no new tweets.\n')
      if open(PROJECT+'.busy').read()=='stop':
        tweets=write_tweets(tweets,True)
        serialize()
        sys.exit(0)
      log.flush()
    serialize()
    iterations+=1
    log.write('Finished '+str(iterations)+'. iteration out of '+str(ITERATION_COUNT)+'. Number of users is '+str(len(user_index))+', number of tweets '+str(no_tweets)+'.\n')
    if iterations==ITERATION_COUNT or open(PROJECT+'.busy').read()=='stop':
      tweets=write_tweets(tweets,True)
      break
    log.write('Sleeping '+str(SLEEP_BETWEEN_ITERATIONS)+' seconds...\n')
    sleep(SLEEP_BETWEEN_ITERATIONS)


class StdOutListener(StreamListener):

  def __init__(self,log):
    super(StdOutListener, self).__init__()
    self.e420=60
    self.no_tweets=0
    self.log=log
    self.tweets=[]

  def on_status(self,status):
    self.e420=60
    added=False
    if status.coordinates!=None:
      self.tweets.append(status)
      self.no_tweets+=1
      if self.no_tweets%BATCH_SIZE==0:
        self.log.write(datetime.now().isoformat()+'\tTweets collected: '+str(self.no_tweets)+'\n')
        self.tweets=write_tweets(self.tweets)
    self.log.flush()

  def on_error(self,status):
    if status==420:
      self.log.write(datetime.now().isoformat()+'\tERROR 420, sleeping '+str(self.e420)+'\n')
      sleep(self.e420)
      self.e420*=2
    else:
      self.log.write(datetime.now().isoformat()+'\tERROR '+str(status)+', sleeping 5\n')
      sleep(5)
    self.log.flush()

def geo_mode():
  l=StdOutListener(log)
  log.flush()
  auth=OAuthHandler(CONSUMER_KEY,CONSUMER_SECRET)
  auth.set_access_token(ACCESS_TOKEN,ACCESS_TOKEN_SECRET)
  while True:
    try:
      stream=tweepy.Stream(auth,l)
      stream.filter(locations=[MINLON,MINLAT,MAXLON,MAXLAT])
    except:
      log.write(str(sys.exc_info())+'\n')
      log.write(datetime.now().isoformat()+'\tSleeping 0 and restarting\n')
      continue

if __name__=='__main__':
  PROJECT=sys.argv[1]
  if not os.path.isfile(PROJECT+'.py'):
    sys.stderr.write('There is no configuration file '+PROJECT+'.py for project '+PROJECT+'\n')
    sys.exit(1)
  exec('from '+PROJECT+' import *')
  # authorization
  auth = tweepy.OAuthHandler(CONSUMER_KEY,CONSUMER_SECRET)
  auth.set_access_token(ACCESS_TOKEN,ACCESS_TOKEN_SECRET)
  # logging
  log=open(PROJECT+'.log','a')
  #log=sys.stdout # for debugging
  # creating output dir
  if not os.path.isdir(PROJECT):
    os.makedirs(PROJECT)
  # checking the busy file
  log.write('\n\n\n### NEW RUN AT '+datetime.now().isoformat()+' ###\n\n\n')
  if os.path.isfile(PROJECT+'.busy'):
    if open(PROJECT+'.busy').read()=='yes':
      sys.stderr.write('By the content of the "busy" file, the tool seems to be running already.\nDelete the respective file if you are sure that no instance of the tool is running and start the tool again.\n')
      sys.exit(1)
  open(PROJECT+'.busy','w').write('yes')
  # tweet counter
  no_tweets=0
  
  if MODE=='LANG':
    # starting the API
    api=tweepy.API(auth,wait_on_rate_limit=True,wait_on_rate_limit_notify=True,retry_count=3,retry_delay=10)
    # loading seeds
    try:
      seedw=set([e.decode('utf8').strip() for e in open(SEEDS)])
      log.write('Successfully loaded the seed file...\n')
    except:
      sys.stderr.write('Problem with reading the seed file!\n')
      sys.exit(1)
    # loading users
    try:
      user_index=pickle.load(open(PROJECT+'.user_index'))
      log.write('Successfully loaded the old user index file with '+str(len(user_index))+' users...\n')
    except:
      user_index={}
      log.write('Created a new user index...\n')
    lang_mode()

  elif MODE=='GEO':      
    geo_mode()

  else:
    sys.stderr.write('MODE in the configuration file should either be set to "LANG" or "GEO".\n')
    sys.exit(1)

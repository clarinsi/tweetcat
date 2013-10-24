from config import *

import tweepy
import sys
from time import sleep,time
from datetime import datetime
from xml.sax.saxutils import escape
from shutil import move,copy
import cPickle as pickle
import re
import os.path

if os.path.isfile('busy'):
  if open('busy').read()=='yes':
    sys.stderr.write('By the content of the "busy" file, the tool seems to be running already.\nDelete the respective file if you are sure that no instance of the tool is running and start the tool again.\n')
    sys.exit(1)
open('busy','w').write('yes')

auth = tweepy.OAuthHandler(CONSUMER_KEY,CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN,ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)

wait_timeline=5
wait_search=5
wait_friends=60
wait_followers=60

last_timeline=0
last_search=0
last_friends=0
last_followers=0

def lang_id(fetched_timeline):
  if len(fetched_timeline)<100:
    sys.stdout.write(datetime.now().isoformat()+'\tTweets have not passed the size threshold ('+str(len(fetched_timeline))+').\n')
    return False
  tokens=re.findall(r'\w+',' '.join([e.text.lower() for e in fetched_timeline]),re.UNICODE)
  good=0
  all=0.0
  for token in tokens:
    if token in functionw:
      good+=1
    all+=1
  if not good/all>=LANG_ID_THRESHOLD:
    sys.stdout.write(datetime.now().isoformat()+'\tTweets have not passed the language threshold ('+str(good/all)+'): '+' '.join(tokens[:1000]).encode('utf8')+'\n')
  return good/all>=LANG_ID_THRESHOLD

def tweet_to_xml(tweet):
  if tweet.in_reply_to_status_id is not None:
    in_reply_to_status_id=' in_reply_to_status_id="'+str(tweet.in_reply_to_status_id)+'"'
  else:
    in_reply_to_status_id=''
  return ('<tweet id="'+tweet.id_str+'" created_at="'+tweet.created_at.isoformat()+'" retrieved_at="'+datetime.now().isoformat()+'" favorite_count="'+str(tweet.favorite_count)+'" retweet_count="'+str(tweet.retweet_count)+'"'+in_reply_to_status_id+'>\n<screen_name>'+tweet.author.screen_name+'</screen_name>\n<text>'+tweet.text+'</text>\n</tweet>\n').encode('utf8')

def search(term):
  global last_search
  if time()<last_search+wait_search:
    sleep(last_search+wait_search-time()+1)
  last_search=time()
  try:
    result=api.search(term)
  except:
    return []
  return result

def followers(user):
  global last_followers
  if time()<last_followers+wait_followers:
    sleep(last_followers+wait_followers-time()+1)
  last_followers=time()
  try:
    result=user.followers()
  except:
    return []
  return result

def friends(user):
  global last_friends
  if time()<last_friends+wait_friends:
    sleep(last_friends+wait_friends-time()+1)
  last_friends=time()
  try:
    result=user.friends()
  except:
    return []
  return result

def new_user_timeline(screen_name):
  global last_timeline
  if time()<last_timeline+wait_timeline:
    sleep(last_timeline+wait_timeline-time()+1)
  last_timeline=time()
  try:
    user_timeline=api.user_timeline(screen_name,count=200)
  except:
    return None
  if lang_id(user_timeline):
    return user_timeline
  else:
    return False

def user_timeline(screen_name,since_id):
  global last_timeline
  if time()<last_timeline+wait_timeline:
    sleep(last_timeline+wait_timeline-time()+1)
  last_timeline=time()
  try:
    return api.user_timeline(screen_name,since_id=since_id)
  except:
    return

def write_timeline(fetched_timeline):
  output=open('tweets_'+datetime.now().isoformat()[:10],'a')
  for tweet in fetched_timeline:
    output.write(tweet_to_xml(tweet))
  if open('busy').read()=='no':
    serialize()
    sys.stdout.write(datetime.now().isoformat()+'\tStopped via the "busy" file\n')
    sys.exit(0)

def serialize():
  try:
    move('user_index.pickle','user_index.copy.pickle')
  except:
    pass
  pickle.dump(user_index,open('user_index.pickle','w'))

try:
  functionw=set([e.decode('utf8').strip() for e in open('functionw.txt')])
  seedw=set([e.decode('utf8').strip() for e in open('seedw.txt')])
  sys.stdout.write('Successfully loaded the function and seed files...\n')
except:
  sys.stderr.write('Problem with reading function or seed file!\n')
  sys.exit(1)

try:
  user_index=pickle.load(open('user_index.pickle'))
  sys.stdout.write('Successfully loaded the old user index file...\n')
  copy('user_index.pickle','user_index.previous_run.pickle')
  sys.stdout.write('Created a copy of the old user index file...\n')
except:
  user_index={}
  sys.stdout.write('Created a new user index...\n')

iterations=0

while True:
  # iterating through seed words and searching for users
  for seed in seedw:
    for hit in search(seed.strip()):
      if hit.author.screen_name not in user_index:
        fetched_timeline=new_user_timeline(hit.author.screen_name)
        if fetched_timeline is False:
          sys.stdout.write(datetime.now().isoformat()+'\tNew user '+hit.author.screen_name+' found by searching did not pass the language filter.\n')
        elif fetched_timeline is None:
          sys.stdout.write(datetime.now().isoformat()+'\tNew user '+hit.author.screen_name+' found by searching could not be retrieved. He probably has a protected account.\n')
        else:
          sys.stdout.write(datetime.now().isoformat()+'\tFound new user by searching: '+hit.author.screen_name+'\n')
          user_index[hit.author.screen_name]=fetched_timeline[0].id
          write_timeline(fetched_timeline)
          for follower in followers(hit.author):
            if follower.screen_name not in user_index:
              fetched_timeline=new_user_timeline(follower.screen_name)
              if fetched_timeline is False:
                sys.stdout.write(datetime.now().isoformat()+'\tNew user '+follower.screen_name+' found as follower did not pass the language filter.\n')
              elif fetched_timeline is None:
                sys.stdout.write(datetime.now().isoformat()+'\tNew user '+follower.screen_name+' found by searching could not be retrieved. He probably has a protected account.\n')
              else:
                sys.stdout.write(datetime.now().isoformat()+'\tFound new user through followers: '+follower.screen_name+'\n')
                user_index[follower.screen_name]=fetched_timeline[0].id
                write_timeline(fetched_timeline)
          for friend in friends(hit.author):
            if friend.screen_name not in user_index:
              fetched_timeline=new_user_timeline(friend.screen_name)
              if fetched_timeline is False:
                sys.stdout.write(datetime.now().isoformat()+'\tNew user '+friend.screen_name+' found as friend did not pass the language filter.\n')
              elif fetched_timeline is None:
                sys.stdout.write(datetime.now().isoformat()+'\tNew user '+friend.screen_name+' found by searching could not be retrieved. He probably has a protected account.\n')
              else:
                sys.stdout.write(datetime.now().isoformat()+'\tFound new user through friends: '+friend.screen_name+'\n')
                user_index[friend.screen_name]=fetched_timeline[0].id
                write_timeline(fetched_timeline)
  # iterating through all known users
  for screen_name,since_id in user_index.items():
    fetched_timeline=user_timeline(screen_name,since_id)
    if fetched_timeline is None:
      sys.stdout.write(datetime.now().isoformat()+'\tKnown user\'s '+screen_name+' timeline not fetched. Will continue on trying.\n')
      continue
    else:
      if len(fetched_timeline)>0:
        sys.stdout.write(datetime.now().isoformat()+'\tKnown user\'s '+screen_name+' timeline fetched with '+str(len(fetched_timeline))+' new tweets.\n')
        user_index[screen_name]=fetched_timeline[0].id
        write_timeline(fetched_timeline)
      else:
        sys.stdout.write(datetime.now().isoformat()+'\tKnown user\'s '+screen_name+' timeline fetched with no new tweets.\n')
  serialize()
  iterations+=1
  sys.stdout.write('Finished '+str(iterations)+'. iteration out of '+str(ITERATION_COUNT)+'. Number of users is '+str(len(user_index))+'.\n')
  if iterations==ITERATION_COUNT or open('busy').read()=='stop':
    break
  sys.stdout.write('Sleeping '+str(SLEEP_BETWEEN_ITERATIONS)+' seconds...\n')
  sleep(SLEEP_BETWEEN_ITERATIONS)

sys.stdout.write('Deleting the "busy" file and exiting.\n')
open('busy','w').write('no')

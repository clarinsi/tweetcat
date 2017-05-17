#-*-coding:utf8-*-
import re

# path to the harvested data
PATH='../1-harvest/hbs'

# whether to discartd tweets with no user-defined variables extracted
DISCARD_EMPTY=True

### DEFINITION OF NORMALIZATION CONSISTING OF SPECIAL CHARACTER REPLACEMENT AND REPETITION REMOVAL ###
# only change the mappings of special characters (if needed)
SPECIAL={u'č':u'c',u'š':u's',u'ž':u'z',u'ć':u'c',u'đ':u'dj'}
#SPECIAL={} # simply uncomment if no character replacements are to be done
# number of maximum character repetitions to be allowed in the normalized text, 0 leaves everyting intact
MAX_REPETITIONS=1

### DEFINITION OF TOKENIZATION ###
# will be used if external lexical resources are defined for the "lexicon_choice" functionality
# existing definition shoud be reasonable for most space-segmented languages
TOKENS=re.compile(r'#\w+|@\w|https?://[\w/_.-]+|\w+',re.UNICODE)

### DEFINITION OF VARIABLES TO BE EXTRACTED ###
# pairs of arguments from Status objects to be extracted and functions to be applied, None for lambda x:x
# an example of a Status object can be found at the end of this file
EXTRACTION_STATUS=[
                   ("['lang']",None), # language predicted by Twitter
                   ("['created_at']",lambda x:x[-4:]), # year the tweet was published
                   ("['text']",lambda x:str(len(x))), # length of a tweet in characters
                  ]

# pairs of function names and arguments / resources to be run on the tweet text
EXTRACTION_TEXT=[
                ]

# same as previous, but to be run on lowercased text
EXTRACTION_LOWER=[
                  ('lexicon_choice','stosta'),
                  ('regex_choice',((r'\b(da li)\b','dali'),(r'\b(je li)\b','jeli'))),
                 ]

# same as previous, but to be run on normalised text
EXTRACTION_NORMALISED=[
                       ('lexicon_choice','iraisaova'),
                       ('lexicon_choice','rdrop'),
                       ('lexicon_choice','months'),
                       ('regex_choice',((r'\b(treba da)\b','treba'),(r'\btreba(m|s|mo|te|ju)\b|\btreba(?! da)','trebam'))),
                       ('regex_choice',((r'^i\'m at ','noise'),(ur'по курсу','noise'))),
                      ]

### EXAMPLE OF A STATUS OBJECT ###
"""
[
 {
  "contributors": null, 
  "truncated": false, 
  "text": "Near Belgrade, Serbia. Oh, how I wish it's near Madrid, Spain.", 
  "is_quote_status": false, 
  "in_reply_to_status_id": null, 
  "id": 491296909722923008, 
  "favorite_count": 1, 
  "source": "<a href=\"http://twitter.com/download/android\" rel=\"nofollow\">Twitter for Android</a>", 
  "retweeted": false, 
  "coordinates": {
   "type": "Point", 
   "coordinates": [
    20.4842477, 
    44.8097362
   ]
  }, 
  "entities": {
   "symbols": [], 
   "user_mentions": [], 
   "hashtags": [], 
   "urls": []
  }, 
  "in_reply_to_screen_name": null, 
  "id_str": "491296909722923008", 
  "retweet_count": 0, 
  "in_reply_to_user_id": null, 
  "favorited": false, 
  "user": {
   "follow_request_sent": false, 
   "has_extended_profile": false, 
   "profile_use_background_image": true, 
   "time_zone": "Belgrade", 
   "id": 129151258, 
   "default_profile": false, 
   "verified": false, 
   "profile_text_color": "333333", 
   "profile_image_url_https": "https://pbs.twimg.com/profile_images/785238118601547776/v7cundbB_normal.jpg", 
   "profile_sidebar_fill_color": "DDFFCC", 
   "is_translator": false, 
   "geo_enabled": true, 
   "entities": {
    "description": {
     "urls": []
    }
   }, 
   "followers_count": 1549, 
   "protected": false, 
   "id_str": "129151258", 
   "default_profile_image": false, 
   "listed_count": 12, 
   "lang": "en", 
   "utc_offset": 3600, 
   "statuses_count": 13425, 
   "description": "Journalist / Everything is possible. Impossible is nothing/ Nekad sam ozbiljan. Nekad se samo dobro zezam.", 
   "friends_count": 480, 
   "profile_link_color": "3B94D9", 
   "profile_image_url": "http://pbs.twimg.com/profile_images/785238118601547776/v7cundbB_normal.jpg", 
   "notifications": false, 
   "profile_background_image_url_https": "https://abs.twimg.com/images/themes/theme15/bg.png", 
   "profile_background_color": "89C9FA", 
   "profile_banner_url": "https://pbs.twimg.com/profile_banners/129151258/1417217309", 
   "profile_background_image_url": "http://abs.twimg.com/images/themes/theme15/bg.png", 
   "name": "IvanVu.", 
   "is_translation_enabled": false, 
   "profile_background_tile": false, 
   "favourites_count": 10516, 
   "screen_name": "001van", 
   "url": null, 
   "created_at": "Sat Apr 03 10:00:31 +0000 2010", 
   "contributors_enabled": false, 
   "location": "Belgrade, Serbia", 
   "profile_sidebar_border_color": "FFFFFF", 
   "translator_type": "regular", 
   "following": false
  }, 
  "geo": {
   "type": "Point", 
   "coordinates": [
    44.8097362, 
    20.4842477
   ]
  }, 
  "in_reply_to_user_id_str": null, 
  "lang": "en", 
  "created_at": "Mon Jul 21 19:01:25 +0000 2014", 
  "in_reply_to_status_id_str": null, 
  "place": {
   "country_code": "RS", 
   "url": "https://api.twitter.com/1.1/geo/id/58a08d4ddc8aab9f.json", 
   "country": "Republic of Serbia", 
   "place_type": "country", 
   "bounding_box": {
    "type": "Polygon", 
    "coordinates": [
     [
      [
       18.8465131, 
       42.2363014
"""

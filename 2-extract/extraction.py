#-*-coding:utf8-*-
import csv
import re
from langid import classify
import sys
import os
import json
import gzip
repetition_re=re.compile(r'(.)\1+')

def load_resource(path):
  resource=[]
  for line in open(path):
    resource.append(line.strip().decode('utf8').split('\t'))
  return dict(resource)

def replace_special(text,special):
  result=''
  for char in text:
    result+=special.get(char,char)
  return result

def remove_repetitions(text,max):
  if max==0:
    return text
  return repetition_re.sub(r'\1'*max,text)

def tokenize(text,regex):
  return regex.findall(text)

def metadata(status,argument,function):
  if function==None:
    function=lambda x:x
  try:
    return function(eval('status'+argument))
  except:
    return 'NA'

def regex_choice(text,regex_pairs):
  found=set()
  for regex,value in regex_pairs:
    if re.compile(regex,re.UNICODE).search(text)!=None:
      found.add(value)
  if len(found)==1:
    return list(found)[0]
  else:
    return 'NA'

def lexicon_choice(text,resource,tokens):
  value='NA'
  for token in tokenize(text,tokens):
    if token in resource:
      if value=='NA':
        value=resource[token]
      else:
        if value!=resource[token]:
          return 'NA'
  return value

if __name__=='__main__':
  PROJECT=sys.argv[1]
  EXTRACTION_STATUS_DEFAULT=[("['id_str']",None),("['user']['screen_name']",None),("['coordinates']['coordinates'][0]",lambda x:str(x)),("['coordinates']['coordinates'][1]",lambda x:str(x)),("['place']['country_code']",None),("['text']",None),]
  if not os.path.isfile(PROJECT+'.py'):
    sys.stderr.write('There is no configuration file '+PROJECT+'.py for project '+PROJECT+'\n')
    sys.exit(1)
  exec('from '+PROJECT+' import *')
  resources={}
  if os.path.isdir(PROJECT):
    for file in os.listdir(PROJECT):
      resources[file]=load_resource(os.path.join(PROJECT,file))
  out=open(PROJECT+'.csv','w')
  csv_out=csv.writer(out)
  num=0
  for file in os.listdir(PATH):
    for status in json.load(gzip.open(os.path.join(PATH,file))):
      num+=1
      if num%10000==0:
        print 'Processed',num
      entry=[]
      for (argument,function) in EXTRACTION_STATUS_DEFAULT+EXTRACTION_STATUS:
        entry.append(metadata(status,argument,function).encode('utf8'))
      for function,arg in EXTRACTION_TEXT:
        if function=='lexicon_choice':
          entry.append(lexicon_choice(text,resources[arg],TOKENS))
        elif function=='regex_choice':
          entry.append(regex_choice(text,arg))
      text=status['text'].lower()
      for function,arg in EXTRACTION_LOWER:
        if function=='lexicon_choice':
          entry.append(lexicon_choice(text,resources[arg],TOKENS))
        elif function=='regex_choice':
          entry.append(regex_choice(text,arg))
      text=replace_special(remove_repetitions(text,MAX_REPETITIONS),SPECIAL)
      for function,arg in EXTRACTION_NORMALISED:
        if function=='lexicon_choice':
          entry.append(lexicon_choice(text,resources[arg],TOKENS))
        elif function=='regex_choice':
          entry.append(regex_choice(text,arg))
      if DISCARD_EMPTY:
        if len(set(entry[6:]))<2 and 'NA' in entry[6:]:
          continue
      csv_out.writerow(entry)
  out.close()

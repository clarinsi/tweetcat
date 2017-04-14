# The harvesting module of TweetCat

Requirements: python2.7*, tweepy3.5.0 (https://github.com/tweepy/tweepy), langid.py (https://github.com/saffsd/langid.py)

Harvesting can be performed in two different modes:

1. the LANG mode: useful in case we want to collect tweets written in specific langauges
2. the GEO mode: useful in case we want to collect geo-encoded tweets published in a specific geograpic perimeter

The collection process should be run in the background, like ```nohup python harvesting.py hbs &```. The first argument of the script (```hbs```)is the project name. The project configuration is read from the file of the same name, with the ```.py``` extension.

For setting up any mode, you are supposed to make a copy of the exemplary ```hbs.py``` configuration file and name it after your project (naming restrictions are the same as for Python variables). There is another exemplary project, ```us_geo```, which examplifies harvesting in the GEO mode.

In the configuration file you first define your API credentials (obtainable by registering your app at https://apps.twitter.com) and which mode you will be using.

Logging is performed in ```[project_name].log```.  From the log you can follow the number of collected tweets and potential exceptions and errors occurring while communicating with the Twitter API.

For stopping the collection process, just change the content of the ```[project_name].busy``` file to ```stop```.

## The LANG mode

The input for the LANG mode is the following:
- a file with seed words that are frequent and specific for the language of interest; these will be used for identifying users tweeting in the desired language via the search API
- a list of language codes for langid.py (list of codes is available at https://github.com/saffsd/langid.py) that will be used for additional filtering of the identified users

## The GEO mode

The input for the GEO mode is only the geographic perimeter.

Additional filtering of the obtained geo-encoded tweets can be performed later with the ```filter_users.py``` script. Filtering can be done by the criteria of
- language (from https://github.com/saffsd/langid.py) and
- country (https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2)
These criteria are set in the configuration file as well.

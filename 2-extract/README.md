# The extraction module of TweetCat

Requirements: python2.7*

This module enables extracting specific variables from the tweets harvested with the harvesting module. Variables can be very general, like the text of a tweet, the day of week the tweet was published, or very specific such as the presence of a specific linguistic structure.

Similar to the harvesting module, setting the extraction procedure should be performed by editing the Python script named after the project, so in case of the ```hbs``` project the ```hbs.py``` file should be edited. For your own projects, make a copy of that file and adapt it to your needs.

Running the variable extraction process can performed with ```python extraction.py hbs```. 

The variable extraction process is run on two levels:

1. the level of the Status object, enabling extracting tweet metadata such as the text of the tweet, number of replies of the tweet etc.; there is an exemplary Status object in the ```hbs.py``` file available (```EXTRACTION_STATUS```)

2. the level of the text of a tweet, there are three sublevels available:

a. the original text (```EXTRACTION_TEXT```)

b. the lowercased text (```EXTRACTION_LOWER```)

c. the normalized text (```EXTRACTION_NORMALIZED```)

There are two main types of functions for extracting variables from the text of each tweet: ```lexicon_choice``` and ```regex_choice```.

The ```lexicon_choice``` function uses one of the lexical resources placed in the folder named after the project name (```hbs/``` for the exemplary project). Each lexical resource consists of one entry per line, two tab-separated values, the first being the token of interest, the second being the value of the linguistic variable. If in a text tokens covering more than one value of the linguitic variable are found, the ```NA``` value is returned, same as if no token was found in the defined resource.

The ```regex_choice``` function works on the same principles as the ```lexicon_choice``` function, but not with lists of tokens, but with regular expressions mapped to the value of the linguistic variable.

The extraction output is written in a csv file named after the project (```hbs.csv``` in our case). Besides the user-defined variables, for each tweet its id, screen name, longitude, latitude and text are extracted by default.

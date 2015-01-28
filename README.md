twitter-recommender-bot
=======================

The TwitterBot is able to recommend resources based on keywords extracted from twitter status updates using the Twitter Stream and REST API. This Twitter application is used as a distribution channel for recommendations provided by the EEXCESS recommender system. Amongst others, the bot is able to follow the current stream of tweets and can reply with a recommendation after identifying a relevant tweet.

Check out this [abstract] (https://github.com/EEXCESS/Twitter/blob/master/Abstract-TwitterBot.pdf?raw=true) for more information.


#### Setup
* > Python3 required
* Setup database (e.g. MySql)
* Add python dependencies:
  * PyMySql
  * peewee
  * rdflib
  * twitter
  * requests
* Checkout source code
* Create Twitter App with write permissions
* Fill in your information in the Config.py file in the package de.uop.twitterbot
* Run CreateTables.py to create all necessary tables in the database
* Use KeywordUtil.py to modify the keyword set
* Modify Recommender.py if you want to use another recommender
* Run RunTwitterBot.py to start start the bot


### Copyright

The sources are released under The MIT License (MIT).

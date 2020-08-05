#!/usr/bin/python
import requests, json, os, sys
from textblob import TextBlob
from collections import Counter
from twython import Twython, TwythonError
import random

requests.packages.urllib3.disable_warnings()

def computeSentiment(data):
        """ Quick and Dirty Sentiment """

        value = 'Neutral'
        sentiment = TextBlob(data['text']).sentiment.polarity
        if sentiment < 0:
                value = 'Bad'
        elif sentiment > 0:
                value = 'Good'

        return value


def sendToBubbles(data):
        try:
                hashtags = [ tag['text'].encode('utf-8').lower() for tag in data['entities']['hashtags'] ]

                if hashtags:
                        print("sendToBubbles: %s" % repr(hashtags))
                        r = requests.post(url='http://0.0.0.0:%d/bubbles/post' % int(os.getenv('PORT')),
                                data=json.dumps({'trends': hashtags }), headers={'Content-Type': 'application/json'})
        except Exception as e:
                print('Analysis error, found a problem parsing hashtag list: %s' % e)


def sendToPie(data):
        try:
                sentiment = computeSentiment(data)

                r = requests.post(url='http://0.0.0.0:%d/pie/post' % int(os.getenv('PORT')),
                        data=json.dumps({'sentiment': sentiment }), headers={'Content-Type': 'application/json'})
        except Exception as e:
                print('Analysis error, found a problem parsing sentiment: %s' % e)

def retweet(data):
        twitter = Twython(os.getenv('APP_KEY'), os.getenv('APP_SECRET'), os.getenv('OAUTH_TOKEN'), os.getenv('OAUTH_TOKEN_SECRET'), client_args={'verify':False})
        try:
                print("Bot: rewteet: %s" % data['id'])
                twitter.retweet(id = data['id'])
        except Exception as e:
                print ("Bot: rewteet exception: %s" % e)
                print ("Bot: retweeted_status: %s" % data['retweeted_status']['id_str'])
                twitter.retweet(id = data['retweeted_status']['id_str'])

def favorite(data):
        twitter = Twython(os.getenv('APP_KEY'), os.getenv('APP_SECRET'), os.getenv('OAUTH_TOKEN'), os.getenv('OAUTH_TOKEN_SECRET'), client_args={'verify':False})
        print("Bot: create_favorite: %s" % data['id'])
        twitter.create_favorite( id=data['id'] )

def follow(data):
        twitter = Twython(os.getenv('APP_KEY'), os.getenv('APP_SECRET'), os.getenv('OAUTH_TOKEN'), os.getenv('OAUTH_TOKEN_SECRET'), client_args={'verify':False})
        print("Bot: follow: %s %s" % ( data['user']['id_str'], data['user']['screen_name'] ))
        twitter.create_friendship( user_id=data['user']['id_str'] )

def populate(data):
        sendToBubbles(data)
        sendToPie(data)

def process(data):
        try:
                print("Bot: DATA: %s" % data['text'].encode('utf-8'))
        except Exception as e:
                print("Bot: exception: %s" % e)
        populate(data)

        retweetProbability = int(os.getenv("PROBABLE_RETWEET"))
        favoriteProbability = int(os.getenv("PROBABLE_FAVORITE"))
        followProbability = int(os.getenv("PROBABLE_FOLLOW"))
        donothingProbability = int(os.getenv("PROBABLE_DO_NOTHING"))

        choices = [0] * retweetProbability + [1] * favoriteProbability + [2] * followProbability + [3] * donothingProbability
        choice = random.choice(choices)
        choice = 3
        if choice == 0:
                #PROBABLE_RETWEET
                try:
                        retweet(data)
                except Exception as e:
                        print("Bot: rewteet exception: %s" % e)
        elif choice == 1:
                #PROBABLE_FAVORITE
                try:
                        favorite(data)
                except Exception as e:
                        print("Bot: favorite exception: %s" % e)
        elif choice == 2:
                #PROBABLE_FOLLOW
                try:
                        follow(data)
                except Exception as e:
                        print("Bot: follow exception: %s" % e)
        else:
                #PROBABLE_DO_NOTHING
                pass

#---------------------------------------------------------------
#
# stats: keeps track of the tag counts
#
#---------------------------------------------------------------
class bubblestats:
        def __init__(self):
                self.trend_raw = []
                self.trend_count = Counter()
        def update(self, trends=[]):
                # this keeps track of the size of the bubble chart
                if len(self.trend_raw) >= int( os.getenv('MAX_CHART_SIZE') ):
                        self.trend_raw = []
                        self.trend_count = Counter()
                else:
			self.trend_raw.extend(trends)
			self.trend_count = Counter( self.trend_raw )
			top20 = self.trend_count.most_common(20)
			self.trend_raw = []
			for tag, num in top20:
				for i in range(0, num):
					self.trend_raw.append(tag)
			self.trend_count = Counter( self.trend_raw )


        def add(self, trends=[]):
                # this lets the bubble chart grow bigger
                self.trend_count = Counter(trends) + self.trend_count

class piestats:
        def __init__(self):
                self.sentiment_raw = []
                self.sentiment_count = Counter()

        def update(self, sentiment=[]):
                # this keeps track of the size of the pie chart (grows to sys MAXINT size)
                if len(self.sentiment_raw) >= sys.maxint:
                        self.sentiment_raw = []
                        self.sentiment_count = Counter()
                else:
                        self.sentiment_raw.extend(sentiment)
                        self.sentiment_count = Counter( self.sentiment_raw )
                        self.sentiment_count.most_common()
        def add(self, sentiment=[]):
                self.sentiment_count = Counter(sentiment) + self.sentiment_count

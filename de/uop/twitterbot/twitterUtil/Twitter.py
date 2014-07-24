from twitter import *
from persistance import UserDao, UserTweetDao, RecommendationDao, Enums
import Config
from recommender import Recommender
import logging
from keywords import KeywordsUtil


def read_filtered_stream():
    print("- read keywords")
    bwl_map = KeywordsUtil.extract_keywords()

    print("- start iterator")

    query = ""

    for i in range(100):
        query += bwl_map.pop() + ", "

    query = query[:-2]

    print(query)

    twitter_stream = TwitterStream(auth=OAuth(Config.access_token, Config.access_token_secret, Config.api_key,
                                              Config.api_secret), domain='userstream.twitter.com')

    iterator = twitter_stream.statuses.filter(track=query)

    for tweet in iterator:
        if "lang" in tweet and "retweeted_status" not in tweet:
            if "en" == tweet["lang"]:
                text = tweet["text"]
                print(text)


def read_sample_stream():
    print("- read keywords")
    bwl_map = KeywordsUtil.extract_keywords()

    twitter_stream = TwitterStream(auth=OAuth(Config.access_token, Config.access_token_secret, Config.api_key,
                                              Config.api_secret), domain='userstream.twitter.com')

    iterator = twitter_stream.statuses.sample()

    print("- start iterator")
    i = 1
    for tweet in iterator:
        i += 1
        # filter for lang = en and ignore retweets
        if "lang" in tweet and "retweeted_status" not in tweet:
            if "en" == tweet["lang"]:
                text = tweet["text"]

                # remove stopword
                keywords = Recommender.get_keywords(text)
                filtered_keywords = Recommender.eliminate_stopwords(keywords)

                # check if a keyword is in keyword list
                for keyword in filtered_keywords:
                    if keyword.lower() in bwl_map:
                        print(keyword + "     -     " + text)
                        break

        if i % 200 == 0:
            print(i)


def read_stream():
    """ Listens to the user-stream and reacts to mention events with a recommendation.
    """
    twitter_user_stream = TwitterStream(auth=OAuth(Config.access_token, Config.access_token_secret, Config.api_key,
                                                   Config.api_secret), domain='userstream.twitter.com')

    for msg in twitter_user_stream.user():
        logging.info(msg)
        recommend = False

        # check if the the bot was mentioned in the status update
        if "entities" in msg:
            for mention in msg["entities"]["user_mentions"]:
                if mention["screen_name"] == Config.name.replace("@", ""):
                    recommend = True

            if recommend:
                user_id = UserDao.add_user(msg["user"]["screen_name"], msg["user"]["id"])
                UserTweetDao.create_user_tweet(user_id, msg["id"], msg["text"], msg)
                Recommender.get_recommendation()
                distribute_recommendations()


def get_mentions():
    """ Get all mentions from the timeline and store them in the db.
    """
    t = Twitter(auth=OAuth(Config.access_token, Config.access_token_secret, Config.api_key, Config.api_secret))
    mentions = t.statuses.mentions_timeline()

    for mention in mentions:
        user_id = UserDao.add_user(mention["user"]["screen_name"], mention["user"]["id"])

        if UserTweetDao.is_new_user_tweet(mention["id"]):
            UserTweetDao.create_user_tweet(user_id, mention["id"], mention["text"], mention)


def distribute_recommendations():
    """ Distribute new recommendations as status updates on twitter.
    """
    t = Twitter(auth=OAuth(Config.access_token, Config.access_token_secret, Config.api_key, Config.api_secret))
    recs = RecommendationDao.get_new_recommendations()

    for rec in recs:
        try:
            t.statuses.update(status=rec.text, in_reply_to_status_id=rec.userTweet.twitterId)
            RecommendationDao.update_status(rec, Enums.RecommendationStatus.done)
        except Exception as e:
            if "duplicate" in str(e):
                RecommendationDao.update_status(rec, Enums.RecommendationStatus.duplicate)
            else:
                RecommendationDao.update_status(rec, Enums.RecommendationStatus.unable)


def __get_max_url_length():
    t = Twitter(auth=OAuth(Config.access_token, Config.access_token_secret, Config.api_key, Config.api_secret))

    return t.help.configuration()["short_url_length_https"]


def __get_current_limit():
    t = Twitter(auth=OAuth(Config.access_token, Config.access_token_secret, Config.api_key, Config.api_secret))

    print(t.application.rate_limit_status())

    #  TODO does statuses update return something? How many remaining updates possible?

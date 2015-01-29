from twitter import *
from persistance import UserDao, UserTweetDao, RecommendationDao, Enums
import Config
from recommender import Recommender
import logging
from keywords import KeywordsUtil
import random
import time

threshold_domain_expert = 30
number_query_items = 50
rotate_after_hits = 1


def get_timeline_by_id(twitterId, bwl_list):
    t = Twitter(auth=OAuth(Config.access_token, Config.access_token_secret, Config.api_key, Config.api_secret))
    iterator = t.statuses.user_timeline(id=twitterId, count=200)

    i = 0
    for tweet in iterator:
        for key in bwl_list:
            key = key.lower()
            if key in tweet["text"].lower():
                i += 1
                # print(key)

    # print("count: " + str(i))
    return i


def read_twitter():
    print("- read keywords")
    bwl_list = list(KeywordsUtil.extract_keywords())

    while True:
        print("- get mentions")
        get_mentions()
        print("- read stream")
        read_filtered_stream(bwl_list)
        print("- sleep")
        time.sleep(300)  # wait 5 minutes


def read_filtered_stream(bwl_list):
    query = ""

    for i in range(number_query_items):
        query += random.choice(bwl_list) + ","

    query = query[:-1]
    twitter_stream = TwitterStream(auth=OAuth(Config.access_token, Config.access_token_secret, Config.api_key, Config.api_secret), domain='userstream.twitter.com')
    iterator = twitter_stream.statuses.filter(track=query)

    i = 0
    rest_calls = 0
    for tweet in iterator:
        if "lang" in tweet and "retweeted_status" not in tweet:
            if "en" == tweet["lang"]:
                if UserDao.is_new_user(tweet["user"]["id"]):

                    if rest_calls < 5:

                        rest_calls += 1

                        # check if user has multiple tweets with keywords
                        count = get_timeline_by_id(tweet["user"]["id"], bwl_list)

                        if count > threshold_domain_expert:
                            key_list = []

                            for key in bwl_list:
                                key = key.lower()
                                if key in tweet["text"].lower():
                                    key_list.append(key)

                            recs = do_recommendation(tweet, " ".join(key_list), True)

                            if recs > 0:
                                i += 1
                                print("rec found")
                    else:
                        print("rest calls exhausted")
                        break

        if i == rotate_after_hits:
            break


# def read_sample_stream():
#     print("- read keywords")
#     bwl_map = KeywordsUtil.extract_keywords()
#
#     twitter_stream = TwitterStream(auth=OAuth(Config.access_token, Config.access_token_secret, Config.api_key,
#                                               Config.api_secret), domain='userstream.twitter.com')
#
#     iterator = twitter_stream.statuses.sample()
#
#     print("- start iterator")
#     i = 1
#     for tweet in iterator:
#         i += 1
#         # filter for lang = en and ignore retweets
#         if "lang" in tweet and "retweeted_status" not in tweet:
#             if "en" == tweet["lang"]:
#                 text = tweet["text"]
#
#                 # remove stopword
#                 keywords = Recommender.get_keywords(text)
#                 filtered_keywords = Recommender.eliminate_stopwords(keywords)
#
#                 # check if a keyword is in keyword list
#                 for keyword in filtered_keywords:
#                     if keyword.lower() in bwl_map:
#                         print(keyword + "     -     " + text)
#                         break
#
#         if i % 200 == 0:
#             print(i)


def read_stream():
    """ Listens to the user-stream and reacts to mention events with a recommendation.
    """
    twitter_user_stream = TwitterStream(auth=OAuth(Config.access_token, Config.access_token_secret, Config.api_key,
                                                   Config.api_secret), domain='userstream.twitter.com')

    for tweet in twitter_user_stream.user():
        logging.info(tweet)
        recommend = False

        # check if the the bot was mentioned in the status update
        if "entities" in tweet:
            for mention in tweet["entities"]["user_mentions"]:
                if mention["screen_name"] == Config.name.replace("@", ""):
                    recommend = True

            if recommend:
                do_recommendation(tweet)


def do_recommendation(tweet, keyword_list="", delete_fails=False):
    # TODO only persist if there is a recommendation?
    user = UserDao.add_user(tweet["user"]["screen_name"], tweet["user"]["id"])
    nr_distributed = 0

    if not UserTweetDao.is_existing_user_tweet(tweet["id"]):
        if len(keyword_list) > 0:
            tweet_text = keyword_list
        else:
            tweet_text = tweet["text"]

        UserTweetDao.create_user_tweet(user.id, tweet["id"], tweet_text, tweet)
        Recommender.get_recommendation()
        nr_distributed = distribute_recommendations()

        # TODO delete failed
        # if nr_distributed == 0 and delete_fails:
        #
        #     user.delete()
        #     pass

    return nr_distributed


def get_mentions():
    """ Get all mentions from the timeline and store them in the db.
    """
    t = Twitter(auth=OAuth(Config.access_token, Config.access_token_secret, Config.api_key, Config.api_secret))
    mentions = t.statuses.mentions_timeline()

    for tweet in mentions:
        do_recommendation(tweet)


def distribute_recommendations():
    """ Distribute new recommendations as status updates on twitter.
    :return: number of distributed recommendations
    """
    t = Twitter(auth=OAuth(Config.access_token, Config.access_token_secret, Config.api_key, Config.api_secret))
    recs = RecommendationDao.get_new_recommendations()

    number_recs = 0
    for rec in recs:
        number_recs += 1
        try:
            t.statuses.update(status=rec.text, in_reply_to_status_id=rec.userTweet.twitterId)
            RecommendationDao.update_status(rec, Enums.RecommendationStatus.done)
        except Exception as e:

            print(e)
            if "duplicate" in str(e):
                RecommendationDao.update_status(rec, Enums.RecommendationStatus.duplicate)
            else:
                RecommendationDao.update_status(rec, Enums.RecommendationStatus.unable)

    return number_recs


def __get_max_url_length():
    t = Twitter(auth=OAuth(Config.access_token, Config.access_token_secret, Config.api_key, Config.api_secret))

    return t.help.configuration()["short_url_length_https"]


def get_current_limit():
    t = Twitter(auth=OAuth(Config.access_token, Config.access_token_secret, Config.api_key, Config.api_secret))

    print(t.application.rate_limit_status())

    #  TODO does statuses update return something? How many remaining updates possible?

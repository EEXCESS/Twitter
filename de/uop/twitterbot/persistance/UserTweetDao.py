from persistance import MysqlManager, Enums
import datetime
import logging


def create_user_tweet(user_id, twitter_id, tweet_input, raw_input):
    user_tweet = MysqlManager.UserTweet()
    user_tweet.user = user_id
    user_tweet.twitterId = twitter_id
    user_tweet.tweet = tweet_input
    user_tweet.created = datetime.datetime.now()
    user_tweet.updated = datetime.datetime.now()
    user_tweet.status = Enums.UserTweetStatus.new.value
    user_tweet.rawInput = raw_input
    user_tweet.save()

    return user_tweet.id


def get_user_tweet_by_twitter_id(twitter_id):

    try:
        user_tweet = MysqlManager.UserTweet.get(MysqlManager.User.twitterId == twitter_id)
    except MysqlManager.User.DoesNotExist as e:
        logging.exception(e)
        user_tweet = None

    return user_tweet


def is_new_user_tweet(twitter_id):
    tweet = get_user_tweet_by_twitter_id(twitter_id)

    if tweet is not None:
        return False
    else:
        return True


def get_new_user_tweets():
    select = MysqlManager.UserTweet.select().where(MysqlManager.UserTweet.status == Enums.UserTweetStatus.new.value)
    ut = select.execute()

    return ut


def update_status(user_tweet, status):
    user_tweet.status = status.value
    user_tweet.updated = datetime.datetime.now()
    user_tweet.save()

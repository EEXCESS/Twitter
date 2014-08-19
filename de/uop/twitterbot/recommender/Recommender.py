import requests
from persistance import RecommendationDao, UserTweetDao, Enums
import Config
import logging

dev = "http://eexcess-dev.joanneum.at/eexcess-privacy-proxy/api/v1/recommend"
payload_prefix = '{"partnerList":[{"systemId":"ZBW"}],"contextKeywords":['
payload_suffix = ']}'

stop_words = [line.strip() for line in open('english')]

"""
{
   "partnerList":[
       {
          "systemId":"ZBW"
       }
   ],
   "contextKeywords":[
      {
         "text":"graz",
         "weight":0.1,
         "reason":"manual"
      },
      {
         "text":"vienna",
         "weight":0.1,
         "reason":"manual"
      }
   ]
}
"""


def get_recommendation():
    """ retrieves the tweets from the db, gets recommendation and stores them in the db

    :return: nothing
    """
    new_tweets = UserTweetDao.get_new_user_tweets()

    for tweet in new_tweets:
        UserTweetDao.update_status(tweet, Enums.UserTweetStatus.requested)
        rec_input_list = get_rec_input_from_tweet(tweet)

        if len(rec_input_list) > 0:
            recs = recommend(rec_input_list)

            if len(recs) > 0:
                text = get_rec_text_for_tweet(tweet, recs[0])
                RecommendationDao.create_recommendation(tweet.id, recs[0].fullRec, text)
                UserTweetDao.update_status(tweet, Enums.UserTweetStatus.done)
            else:
                UserTweetDao.update_status(tweet, Enums.UserTweetStatus.no_recommendation)


def get_rec_text_for_tweet(tweet, rec):
    """ composes the text for the status update

    :param tweet: the original tweet, used to mention the user
    :param rec: the recommendation
    :return: the status update text
    """
    twitter_max_length = 23  # Twitter.getMaxUrlLength()
    url_length = min(len(rec.uri), twitter_max_length)
    text = "Hey @" + tweet.user.username + ", I recommend you: "
    prefix_length = len(text) + url_length + 1
    length_left = 140 - prefix_length

    if len(rec.title) > length_left:
        desc = rec.title[0:length_left - 2] + "..."
    else:
        desc = rec.title

    text = text + rec.uri + " " + desc

    return text


def get_rec_input_from_tweet(tweet):
    """ extracts the relevant keywords from the tweet

    :param tweet: the tweet containing the tweet text
    :return: a list of recInput objects
    """
    # t = ast.literal_eval(tweet.rawInput)
    # print(tweet.rawInput)
    # print(t["entities"]["hashtags"])
    # print(t["entities"]["user_mentions"])

    keywords = get_keywords(tweet.tweet)
    filtered_keywords = eliminate_stopwords(keywords)

    rec_input_list = []

    for keyword in filtered_keywords:
        rec_input = RecInput()
        rec_input.text = keyword
        rec_input.weight = 1.0
        rec_input_list.append(rec_input)

    return rec_input_list


def eliminate_stopwords(keywords):
    """ Eliminates english stopwords

    :param keywords: the input keywords possibly containing stopwords
    :return: stopword free keywords
    """
    filtered_keywords = []

    for keyword in keywords:
        if keyword.lower() not in stop_words:
            filtered_keywords.append(keyword)

    return filtered_keywords


def get_keywords(tweet):
    """ extracts all words from the tweet removing unwanted chars

    :param tweet: the tweet text
    :return: a list of words
    """
    # remove mention of the bot
    tweet = tweet.replace(Config.name, "")
    # remove #, @, ...
    remove_list = ["#", "@", ".", "!", "?", "-", "_", "+", "<", ">"]

    for remove_char in remove_list:
        tweet = tweet.replace(remove_char, "")

    return tweet.split()


def recommend(list_rec_input):
    """ Generates the payload and calls the recommender

    :param list_rec_input: list of recInput objects
    :return: a list of recommendations, maybe empty
    """
    #generate payload
    payload = generate_payload(list_rec_input)
    # print("payload: " + payload)

    r = None

    try:
        # Query backend
        r = requests.post(dev, data=payload)
        # print("response: " + str(r.json()))
    except Exception as e:
        print(e)
        logging.exception(e)

    recs = []

    if r is not None:
        # extract recs
        recs = extract_recommendation(r.json())
        #print("recommendation: " + recommendation.getURI() + " - " + recommendation.getTitle())

    return recs


def generate_payload(list_rec_input):
    """ Generates the payload for the recommender call

    :param list_rec_input: list of recInput objects
    :return: the payload string
    """
    payload = payload_prefix

    for rec_input in list_rec_input:
        payload += '{"weight":"' + str(rec_input.weight) + '","text":"' + rec_input.text + '"},'

    # remove last comma
    payload = payload[:-1]
    payload += payload_suffix

    return payload


def extract_recommendation(json):
    """ extracts the recommendation from the recommender response

    :param json: the json response from the recommender service
    :return: a list of recommendations, maybe empty
    """
    recs = []

    if int(json["totalResults"]) > 0:
        results = json["result"]

        for result in results:
            recommendation = Recommendation()
            recommendation.uri = result["uri"]
            recommendation.title = result["title"]
            recommendation.fullRec = json
            recs.append(recommendation)

    return recs


class Recommendation:
    def __init__(self):
        self.title = None
        self.uri = None
        self.fullRec = None


class RecInput:
    def __init__(self):
        self.text = None
        self.weight = None

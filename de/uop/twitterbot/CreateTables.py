from persistance import MysqlManager
import logging

logging.basicConfig(filename='twitterBot.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

try:
    MysqlManager.User.create_table()
    MysqlManager.UserTweet.create_table()
    MysqlManager.Recommendation.create_table()
except Exception as e:
    print(e)
    logging.exception(e)

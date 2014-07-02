from twitterUtil import Twitter
import logging

logging.basicConfig(filename='twitterBot.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

try:
    Twitter.read_stream()
except Exception as e:
    print(e)
    logging.exception(e)















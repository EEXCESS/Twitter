from twitterUtil import Twitter
import logging

logging.basicConfig(filename='twitterBot.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


# TODO Check for hangup: {'hangup': True}

try:
    Twitter.read_stream()
    # Twitter.read_filtered_stream()
except Exception as e:
    print(e)
    logging.exception(e)















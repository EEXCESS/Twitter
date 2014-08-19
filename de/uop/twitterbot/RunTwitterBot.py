from twitterUtil import Twitter
import logging
import time

logging.basicConfig(filename='twitterBot.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

while True:
    try:
        # Twitter.read_stream()
        # Twitter.read_filtered_stream()
        # Twitter.read_sample_stream()
        Twitter.read_twitter()
        # Twitter.get_current_limit()
        # Twitter.get_mentions()
    except Exception as e:
        print(e)
        logging.exception(e)

    time.sleep(600)  # wait 10mins
    logging.info("Reconnect to Twitter stream.")


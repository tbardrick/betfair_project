# importing packages
import betfairlightweight
import json
import os

import queue
import threading
import logging
from tenacity import retry, wait_exponential

from betfairlightweight import StreamListener
from betfairlightweight import BetfairError

# defining certs path 
script_dir = os.path.dirname(os.path.abspath(__file__))
certs_path = os.path.join(script_dir, 'certs')

# setup logging
logging.basicConfig(level=logging.INFO)  # change to DEBUG to see log all updates
logger = logging.getLogger(__name__)


def trading_instance():
    ''' 
    Connect to the api.

    Requires 'api_logins.json' file and certs folder in current directory.
    '''
    with open('api_logins.json') as f:
        login_dict =  json.load(f)

    trading = betfairlightweight.APIClient(username=login_dict['my_username'],
                                           password=login_dict['my_password'],
                                           app_key=login_dict['my_app_key'],
                                           certs=certs_path)

    return(trading)

class Streaming(threading.Thread):
    def __init__(
        self,
        client: betfairlightweight.APIClient,
        market_filter: dict,
        market_data_filter: dict,
        conflate_ms: int = None,
        streaming_unique_id: int = 10000, # 10 seconds
    ):
        threading.Thread.__init__(self, daemon=True, name=self.__class__.__name__)
        self.client = client
        self.market_filter = market_filter
        self.market_data_filter = market_data_filter
        self.conflate_ms = conflate_ms
        self.streaming_unique_id = streaming_unique_id
        self.stream = None
        self.output_queue = queue.Queue()
        self.listener = StreamListener(output_queue=self.output_queue)

    @retry(wait=wait_exponential(multiplier=1, min=2, max=20))
    def run(self) -> None:
        logger.info("Starting MarketStreaming")
        self.client.login()
        self.stream = self.client.streaming.create_stream(
            unique_id=self.streaming_unique_id, listener=self.listener
        )
        try:
            self.streaming_unique_id = self.stream.subscribe_to_markets(
                market_filter=self.market_filter,
                market_data_filter=self.market_data_filter,
                conflate_ms=self.conflate_ms,
                initial_clk=self.listener.initial_clk,  # supplying these two values allows a reconnect
                clk=self.listener.clk,
            )
            self.stream.start()
        except BetfairError:
            logger.error("MarketStreaming run error", exc_info=True)
            raise
        except Exception:
            logger.critical("MarketStreaming run error", exc_info=True)
            raise
        logger.info("Stopped MarketStreaming {0}".format(self.streaming_unique_id))

    def stop(self) -> None:
        if self.stream:
            self.stream.stop()
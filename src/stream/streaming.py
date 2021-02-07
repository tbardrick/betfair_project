import logging
import queue
import threading
from utils import bf_utils
import betfairlightweight
from betfairlightweight.filters import (
    streaming_market_filter,
    streaming_market_data_filter,
)


# setup logging
logging.basicConfig(level=logging.INFO)  # change to DEBUG to see log all updates

# create trading instance (app key must be activated for streaming)
trading = bf_utils.api_login()

# grab a horse race 
test_market = bf_utils.grab_market_id()

# create queue
output_queue = queue.Queue()

# create stream listener
listener = betfairlightweight.StreamListener(output_queue=output_queue)

# create stream
stream = trading.streaming.create_stream(listener=listener)

# create filters (GB WIN racing)
market_filter = streaming_market_filter(
     market_ids = [test_market]
)
market_data_filter = streaming_market_data_filter(
    fields=["EX_MARKET_DEF", "EX_BEST_OFFERS"], ladder_levels=3
)

# subscribe
streaming_unique_id = stream.subscribe_to_markets(
    market_filter=market_filter,
    market_data_filter=market_data_filter,
    conflate_ms=1000,  # send update every 1000ms
)

# start stream in a new thread (in production would need err handling)
t = threading.Thread(target=stream.start, daemon=True)
t.start()

# check for updates in output queue
while True:
    market_books = output_queue.get()

    # market_books = listener.snap(
    #     market_ids=[test_market]
    # )

    for market_book in market_books:
        print(
            # market_book,
            # market_book.streaming_unique_id,  # unique id of stream (returned from subscribe request)
            # market_book.streaming_update,  # json update received
            # market_book.market_definition,  # streaming definition, similar to catalogue request
            # market_book.publish_time  # betfair publish time of update
        )
        print([r.ex.available_to_back[0].price if r.ex.available_to_back else 1.01 for r in market_book.runners])
        # print(market_book.runners)


# PRICE INFO
# 1ST IN LIST SEEMS TO ALWAYS BE '0' - Nope, this specifies the ladder level

# EACH PRICE IS IN THE SAME LIST AS IT'S SIZE

# access market_boko to get all prices as opposed to just printing updates


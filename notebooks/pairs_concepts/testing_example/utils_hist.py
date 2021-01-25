import pandas as pd
from betfairlightweight import StreamListener
from betfairlightweight.streaming.stream import MarketStream
import betfairlightweight


# defining data to read in
datadict = {'Time': [],
       'MarketId' : [],
       'Status' : [],
       'Inplay' : [], 
       'SelectionId' : [],
       'LastPriceTraded' : [],
       'RunnerStatus' : []
}


# defining streaming functions
class HistoricalStream(MarketStream):
    # create custom listener and stream

    def _init_(self, listener):
        super(HistoricalStream, self)._init_(listener)

    def on_process(self, market_books):
        for market_book in market_books:
            for runner in market_book.runners:

                datadict['Time'].append(market_book.publish_time)
                datadict['MarketId'].append(float(market_book.market_id))
                datadict['Status'].append(market_book.status)
                datadict['Inplay'].append(market_book.inplay)
                datadict['SelectionId'].append(runner.selection_id)
                datadict['LastPriceTraded'].append(runner.last_price_traded)
                datadict['RunnerStatus'].append(runner.status)

class HistoricalListener(StreamListener):
    def _add_stream(self, unique_id, stream_type):
        if stream_type == "marketSubscription":
            return HistoricalStream(self)

listener = HistoricalListener(max_latency=None)

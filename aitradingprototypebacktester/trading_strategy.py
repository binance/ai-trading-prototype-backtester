from backtesting import Strategy
import pandas as pd
from aitradingprototypebacktester.config_loader import load_config
import logging


class TradingStrategy(Strategy):
    """
    This class defines the trading strategy for the backtesting.py library.

    Strategy:
        If the sentiment is bullish and the current balance of the base currency is 0, a buy order with size = `order_quantity` is placed.
        If the sentiment is bullish and the current balance of the base currency is not 0, a buy order is not placed, because last order was already a buy order.

        If the sentiment is bearish and the current balance of the base currency is > 0, then a sell order for entire balance is placed.
        If the sentiment is bearish and the current balance of the base currency is 0, then a sell order is not placed, because last order was already a sell order.
    """

    def init(self):
        """
        Initialise the TradingStrategy class with the sentiment data.
        Set the order size to the value specified in the config.yaml file in terms of satoshis.
        """
        config = load_config("config.yaml")
        logging_level = config["logging_level"]
        logging.basicConfig(level=logging_level)
        # Convert config["order_quantity"] to satoshis
        self.order_quantity = config["order_quantity"] * 1e6
        self.sentiment_data = pd.read_csv(
            config["sentiment_data"],
            names=["timestamp", "headline", "sentiment"],
            index_col=0,
        )

        self.sentiment_data.index = pd.to_datetime(self.sentiment_data.index, unit="ms")
        self.last_order = None

    def next(self):  #
        """
        Iterates through each candle/kline in the date-range and checks if corresponding headline data exists for the specific time.
        Based on the sentiment data, the strategy will determine the appropriate action to take:
        - If the sentiment is "bullish" and the last order was not a "buy", a buy order is placed.
        - If the sentiment is "bearish" and the last order was not a "sell" or None, the position is closed.
        """
        kline_open_timestamp = pd.Timestamp(self.data.index[-1]).tz_localize(None)
        try:
            previous_kline_open_timestamp = pd.Timestamp(
                self.data.index[-2]
            ).tz_localize(None)
            sentiment = (
                self.sentiment_data.loc[
                    (self.sentiment_data.index <= kline_open_timestamp)
                    & (self.sentiment_data.index > previous_kline_open_timestamp)
                ]
                .tail(1)["sentiment"]
                .values[0]
            )
        except:
            sentiment = "Null"
        if sentiment == "bullish" and self.last_order != "buy":
            logging.info(f"Placing buy order at {kline_open_timestamp}")
            self.buy(size=self.order_quantity)
            self.last_order = "buy"
        elif (
            sentiment == "bearish"
            and self.last_order != "sell"
            and self.last_order != None
        ):
            logging.info(f"Placing sell order at {kline_open_timestamp}")
            self.position.close()
            self.last_order = "sell"

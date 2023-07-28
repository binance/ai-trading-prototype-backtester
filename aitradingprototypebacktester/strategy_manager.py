import logging

import pandas as pd
from backtesting import Strategy

from aitradingprototypebacktester.strategy.successive_strategy import SuccessiveStrategy
from aitradingprototypebacktester.strategy.tb_enums import OrderAction, OrderSide

from aitradingprototypebacktester.config_loader import load_config


class StrategyManager(Strategy):
    """
    Strategy Manager
    ----------------
    This class inherits from the backtesting library's `Strategy` class and provides a mechanism to manage trading
    decisions based on sentiment data and a successive trading strategy.
    """

    def init(self):
        """
        Initializes the object by loading the configuration from the "config.yaml" file and setting up the logging level.
        """
        config = load_config("config.yaml")
        logging_level = config["logging_level"]
        logging.basicConfig(level=logging_level, format="%(message)s")
        # Convert config["order_quantity"] and config["total_quantity_limit"] to satoshis
        self.order_quantity = config["order_quantity"] * 1e6
        self.total_quantity_limit = config["total_quantity_limit"] * 1e6
        self.sentiment_data = pd.read_csv(
            config["sentiment_data"],
            names=[
                "source",
                "collected_timestamp",
                "published_timestamp",
                "headline",
                "sentiment",
            ],
            quotechar='"',
            skipinitialspace=True,
        )

        # If the published_timestamp is in seconds (i.e., less than 10**10), convert it to Milliseconds.
        self.sentiment_data.loc[
            self.sentiment_data["published_timestamp"] < 10**10, "published_timestamp"
        ] *= 1000

        # Set the published_timestamp as the index
        self.sentiment_data.set_index("published_timestamp", inplace=True)
        # Convert the ms timestamp to datetime format in order to be compatible with backtesting library
        self.sentiment_data.index = pd.to_datetime(self.sentiment_data.index, unit="ms")
        self.successive_strategy = SuccessiveStrategy(
            {
                "symbol": config["symbol"],
                "order_quantity": self.order_quantity,
                "total_quantity_limit": self.total_quantity_limit,
            }
        )

    def next(self):
        """
        Passes the sentiment to the trading strategy and executes trading decisions based on this strategy.

        This method is called for each time step in the backtesting process and makes trading decisions based on the
        sentiment data and the successive strategy. It determines whether to place a buy or sell order, or to skip the
        order for the current time step.
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
            sentiment = "unknown"
        strategy_decision = self.successive_strategy.order_strategy(
            sentiment, self.position.size
        )
        if strategy_decision["action"] == OrderAction.POST_ORDER:
            # Order is to be placed
            order = strategy_decision["order"]
            if order["side"] == OrderSide.BUY.value:
                # Place buy order for config-defined order quantity
                logging.info(f"Placing buy order at {kline_open_timestamp}")
                self.buy(size=order["quantity"])
            elif order["side"] == OrderSide.SELL.value:
                # Place sell order for config-defined order quantity
                logging.info(f"Placing sell order at {kline_open_timestamp}")
                self.sell(size=order["quantity"])
        elif strategy_decision["action"] == OrderAction.SKIP_ORDER:
            # No sentiment for this kline, skip order
            pass

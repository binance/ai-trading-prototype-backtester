# AI Trading Prototype Backtester

This project is a backtester for the sentiment-analysis cryptocurrency trading strategy that pairs with the live trading bot, [ai-trading-prototype](https://github.com/binance/ai-trading-prototype/). This backtester is designed to run accurate simulations for a given date range on a chosen trading symbol.

![Diagram](../assets/diagram.png?raw=true)

## Disclaimer

This trading bot backtester does not provide financial advice or endorse trading strategies. Users assume all risks, as past results from historical data do not guarantee future returns; the creators bear no responsibility for losses. Please seek guidance from financial experts before trading or investing. By using this project you accept these conditions.

## Features

* A flexible trading strategy builder.
* Customisable Backtesting strategy.
* Automated data downloader using `data.binance.vision`.
* Detailed backtest results and performance assessment, including HTML visualisations of all trades.

## Installation

1. Clone the repository
```
git clone https://github.com/binance/ai-trading-prototype-backtester
```
2. Move into the cloned directory
```
cd ai-trading-prototype-backtester
```
3. Install dependencies
```
pip install -r requirements.txt
```

## Usage
### Configuration

All configurations are stored in `config.yaml.example`. You can specify:
* `symbol`: The trading symbol/ pair. Example: `ETHUSDT`.
* `kline_interval`: The interval of the candlesticks. Valid intervals are: `1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h` or `1d`
* `start_date` and `end_date`: The range of dates to backtest on. Format: `YYYY-MM-DD`.
* `sentiment_data`: The path to the sentiment data file. Default: `./sentiment_data/sentiment_data.csv`.
* `start_balance`: The starting balance in quote currency (eg. USDT). Default: `100000`.
* `order_size`: The order size in base currency (eg. BTC). Default: `0.01`.
* `total_quantity_limit`: The maximum quantity of base currency (eg. BTC) that can be held at any given time. Default: `1`.
* `commission`: The trading fee/commission ratio. Default: `0.002`.
* `logging_level`: The logging detail level. Default: `INFO`.

Please also ensure that the sentiment data file `sentiment_data.csv` is present and formatted as `"headline source","headline collected timestamp (ms)","headline published timestamp (ms)","headline","sentiment"`.

#### Strategy Configuration Profiles

Within the `strategy_configuration` directory, there are 3 extra configuration files. Each file corresponds to a different strategy/risk level (Aggressive, Conservative and Standard). These can be used to quickly test different parameters with varying degrees of risk.

### Run the backtester as module

```
python -m aitradingprototypebacktester
```

#### How it works

* During the backtesting process, the backtester checks `/sentiment_data/sentiment_data.csv` for a published headline at each kline/candlestick interval.
* If a headline was published during the current time-period, it reads the sentiment of the headline.
* By default, the backtester uses the `successive_strategy` which is defined in `aitradingprototypebacktester/strategy/successive_strategy.py`. The details of how this strategy works is as follows:
  * If the sentiment was "bullish" (meaning it is expected that the price would increase) it will attempt a BUY order of size = `order_size` of base currency, so long as the `total_quantity_limit` (max. quantity that can be held at any given time) has not yet been reached.
  * If the sentiment was "bearish" (meaning that a fall in price is expected), it will attempt to SELL `order_size` quantity of the base currency, so long as the current base currency balance is > 0.
* Once the backtest is complete, it will return a detailed table of results along with an HTML visualisation of all the buys and sells plotted against the trading symbol's price throughout the period.
  * An image, `backtest_result.png`, will also be generated. This is a static view of the HTML visualisation.
* If there is a position still open at the end of the backtest, it will be closed at the open price of the last kline in the backtesting period.

## Backtest Results

* As outlined in the `How it works` section above, the backtester will output several files as a result of each backtest:
  * `output/raw/backtest_result.txt` - A summary of the backtest.
  * `output/raw/backtest_trades.txt` - A detailed list of each individual trade executed during the backtest.
  * `output/visualisation/dynamic_report.html` - HTML visualisation of all the buys and sells plotted against the trading symbol's price throughout the period.
  * `output/visualisation/backtest_result.png` - A static view of the HTML visualisation (image below).

![Backtest Result](../assets/backtest_result.png?raw=true)
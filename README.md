# AI Trading Prototype Backtester

This project is a backtester for the sentiment-analysis cryptocurrency trading strategy that pairs with the live trading bot, [ai-trading-prototype](https://github.com/binance/ai-trading-prototype/). This backtester is designed to run accurate simulations for a given date range on a chosen trading symbol.

### Features

* A flexible trading strategy builder.
* Detailed backtesting results and performance assessment.
* Customizable Backtesting Strategy.
* Detailed HTML visualisations of all trades.
* Automated data downloader using data.binance.vision.

## Project Structure

### Main Components

1. `aitradingprototypebacktester/main.py`
2. `aitradingprototypebacktester/data_downloader.py`
3. `aitradingprototypebacktester/trading_strategy.py`
4. `aitradingprototypebacktester/config_loader.py`
5. `config.yaml`

### Workflow

1. main.py loads our configuration values (symbol, kline_interval, start_date, end_date) from config.yaml.
2. It uses data_downloader.py to automate the process of downloading Binance data (OHLCV) for our defined symbol for the period specified using the end_date and start_date.
3. An instance of the Backtesting class is created with our historical trading data and TradingStrategy. The backtest is run and the results are output in our terminal.
4. Finally, an HTML visualisation of the results from our backtest is saved as "backtest_results.png".

## How It Works

* During the backtesting process, the backtester checks `/sentiment_data/sentiment_data.csv` for a published headline at each kline/candlestick interval.
* If a headline was published during the current time-period, it reads the sentiment of the headline.
* If the sentiment was "bullish" (meaning it is expected that the price would increase) it will attempt a BUY order of size = `order_size` of base currency, so long as the current base currency balance is 0.
* If the sentiment was "bearish" (meaning that a fall in price is expected), it will attempt to SELL 100% of the base currency balance, so long as the current base currency balance is > 0 (ie. the last order was a BUY order).
* Once backtesting is complete, it will return a detailed table of results along with an HTML visualisation of all the buys and sells plotted against the trading symbol's price throughout the period.
  * An image, `backtest_result.png`, will also be generated. This is a static view of the HTML visualisation.
* If there is a position still open at the end of the backtest, it will be closed at the open price of the last kline in the backtesting period.

## Quick Start

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
3. Copy `config_example.yaml`, name it `config.yaml` and edit it with your desired trading symbol, timeframe and kline/candlestick interval, etc.
```yaml
symbol: BTCUSDT # Trading symbol
start_balance: 100000 # Starting balance in quote currency (USDT) (Ensure balance > 1 max base_currency_price as min. order size is 1)
order_size: 0.01 # Order size in base currency (BTC)
commission: 0.002 # Trading fee/commission ratio
kline_interval: 1m # Kline/candlestick interval
start_date: 2023-05-30 # Start date of backtest
end_date: 2023-07-01 # End date of backtest
sentiment_data: ./sentiment_data/sentiment_data.csv # Path to sentiment data file
logging_level: INFO # Logging detail level
```
4. Run the backtester as module
```
python -m aitradingprototypebacktester
```

## Configuration

All configurations are stored in `config.yaml`. You can specify:
* `symbol`: The trading symbol/ pair. Example: `ETHUSDT`.
* `kline_interval`: The interval of the candlesticks. Valid intervals are: `1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h` or `1d`
* `start_date` and `end_date`: The range of dates to backtest on. Format: `YYYY-MM-DD`.
* `sentiment_data`: The path to the sentiment data file. Default: `./sentiment_data/sentiment_data.csv`.
* `start_balance`: The starting balance in quote currency (eg. USDT). Default: `100000`.
* `order_size`: The order size in base currency (eg. BTC). Default: `0.01`.
* `commission`: The trading fee/commission ratio. Default: `0.002`.
* `logging_level`: The logging detail level. Default: `INFO`.

Please also ensure that the sentiment data file `sentiment_data.csv` is present and formatted as `timestamp, headline, sentiment`.

## Disclaimer

The use of this software may result in financial loss. No strategy is 100% accurate. Use it at your own risk. The developer does not take any responsibility for any financial losses that could occur through the use of this bot.
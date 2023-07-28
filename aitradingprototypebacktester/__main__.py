import logging
import os
import bokeh
from backtesting import Backtest
from aitradingprototypebacktester.config_loader import load_config
from aitradingprototypebacktester.data_downloader import download_binance_data
from aitradingprototypebacktester.trading_strategy import TradingStrategy


def initialise_config(config):
    """
    Loads configuration values from config.yaml and returns neccessary variables
    """
    symbol = config["symbol"]
    kline_interval = config["kline_interval"]
    start_date = config["start_date"]
    end_date = config["end_date"]
    start_balance = int(config["start_balance"])
    commission = float(config["commission"])
    logging_level = config["logging_level"]
    return (
        symbol,
        kline_interval,
        start_date,
        end_date,
        start_balance,
        commission,
        logging_level,
    )


def create_directories():
    """
    Check if "output/visualisation" and "output/raw" directories exist, if not create them
    """
    if not os.path.exists("output/visualisation"):
        os.makedirs("output/visualisation")
    if not os.path.exists("output/raw"):
        os.makedirs("output/raw")


def write_results(results):
    """
    Write the backtest results and individual trades to output/raw directory separate text files.
    """
    create_directories()
    with open("output/raw/backtest_result.txt", "w") as file:
        file.write(str(results))
    with open("output/raw/backtest_trades.txt", "w") as file:
        file.write(str(results._trades))


def convert_from_satoshi(results, bt):
    """
    Convert the columns `Size`, `EntryPrice`, `ExitPrice`, `Open`, `High`, `Low`, `Close`, and `Volume` from satoshis back to their original values.

    Args:
        results (object): The `results` object that contains the trades data.
        bt (object): The `bt` object that contains the data for the strategy.

    Returns:
        tuple: A tuple containing the modified `results` object and the modified `bt` object.
    """
    # Convert columns: Size, EntryPrice, ExitPrice,  back from satoshis:
    results._trades = results._trades.assign(
        Size=results._trades.Size / 1e6,
        EntryPrice=results._trades.EntryPrice * 1e6,
        ExitPrice=results._trades.ExitPrice * 1e6,
    )
    bt._data = bt._data.assign(
        Open=results._strategy._data._Data__df.Open * 1e6,
        High=results._strategy._data._Data__df.High * 1e6,
        Low=results._strategy._data._Data__df.Low * 1e6,
        Close=results._strategy._data._Data__df.Close * 1e6,
        Volume=results._strategy._data._Data__df.Volume / 1e6,
    )
    return results, bt


if __name__ == "__main__":
    """
    - Loads configuration values from config.yaml
    - Downloads binance kline/candlestick data from data.binance.vision
    - Creates a Backtest instance with the trading data and trading strategy
    - Runs backtest, outputs results and creates html + png visualisation of results
    - Saves raw backtest results and individual trades
    """
    config = load_config("config.yaml")
    (
        symbol,
        kline_interval,
        start_date,
        end_date,
        start_balance,
        commission,
        logging_level,
    ) = initialise_config(config)
    logging.basicConfig(level=logging_level)  # Initialise Logging
    kline_data = download_binance_data(
        symbol, kline_interval, start_date, end_date, logging_level
    )
    kline_data = (kline_data / 1e6).assign(
        Volume=kline_data.Volume * 1e6  # Convert relevant columns to satoshis
    )
    bt = Backtest(
        kline_data, TradingStrategy, cash=start_balance, commission=commission
    )
    logging.info("Running Backtest...")
    results = bt.run()
    results, bt = convert_from_satoshi(
        results, bt
    )  # Convert relevant columns back from satoshis
    logging.info(results)
    write_results(results)
    plot = bt.plot(resample=False, filename="output/visualisation/dynamic_report.html")
    bokeh.io.export.export_png(
        plot, filename="output/visualisation/backtest_result.png"
    )

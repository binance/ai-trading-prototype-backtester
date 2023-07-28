import requests
import pandas as pd
import datetime
import logging
import os
from io import BytesIO
from zipfile import ZipFile


def get_kline_data(symbol, kline_interval, date_str):
    """
    Fetches the binance data for given symbol and kline-interval for a particular day
    """
    url = f"https://data.binance.vision/data/spot/daily/klines/{symbol.upper()}/{kline_interval}/{symbol.upper()}-{kline_interval}-{date_str}.zip"
    response = requests.get(url)
    return response


def parse_data(response):
    """
    Parses the fetched data and appends it into the list 'data'
    """
    data = []
    with ZipFile(BytesIO(response.content)) as zip_file:
        for file in zip_file.namelist():
            with zip_file.open(file) as f:
                df = pd.read_csv(f, usecols=range(6))
                df.columns = ["Timestamp", "Open", "High", "Low", "Close", "Volume"]
                data.append(df)
    return data


def process_data(data):
    """
    Processes the list into a DataFrame
    """
    df = pd.concat(data)
    df.columns = ["Timestamp", "Open", "High", "Low", "Close", "Volume"]
    df["Timestamp"] = pd.to_datetime(df["Timestamp"], unit="ms")
    df.set_index("Timestamp", inplace=True)
    df.sort_index(ascending=True, inplace=True)
    return df


def load_csv_data(file_path):
    """
    Loads the DataFrame from the specified csv file.
    """
    return pd.read_csv(file_path, index_col=[0])


def download_binance_data(symbol, kline_interval, start_date, end_date, logging_level):
    """
    Downloads Binance data for a given symbol and date range.

    Args:
        symbol (str): The symbol to download data for.
        kline_interval (str): The interval of the kline data.
        start_date (datetime.date): The start date of the data to download.
        end_date (datetime.date): The end date of the data to download.
    """
    logging.basicConfig(level=logging_level)  # Initialise Logging
    market_data_path = f"market_data/{symbol.upper()}/{kline_interval}"

    # Check if the downloads directory exists, create it if it doesn't
    if not os.path.exists(market_data_path):
        os.makedirs(market_data_path)

    data = []
    total_days = (end_date - start_date).days + 1
    downloaded_days = 0

    while start_date <= end_date:
        date_str = start_date.strftime("%Y-%m-%d")
        file_path = f"{market_data_path}/{date_str}.csv"

        # Check if data is already downloaded
        if os.path.isfile(file_path):
            df = load_csv_data(file_path)
            data.append(df)
            logging.info(f"Loaded data for {date_str} from disk.")
            downloaded_days += 1
        else:
            response = get_kline_data(symbol, kline_interval, date_str)

            if response.status_code == 200:
                data += parse_data(response)

                # Save processed data to csv file
                data[-1].to_csv(file_path)

                downloaded_days += 1
                logging.info(
                    f"Downloaded and saved kline data for {date_str}\nProgress: {downloaded_days}/{total_days} days ({(downloaded_days/total_days)*100:.2f}%) downloaded.\n"
                )
            else:
                logging.error(
                    f"Failed to download kline data for date {date_str}. Status code: {response.status_code}"
                )
                downloaded_days += 1
                pass

        start_date += datetime.timedelta(days=1)
    return process_data(data)

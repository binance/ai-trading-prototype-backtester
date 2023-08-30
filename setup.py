from setuptools import setup

setup(
    name="aitradingprototypebacktester",
    version="1.0.0",
    description="AI Trading Prototype Backtester",
    author="Binance",
    packages=["aitradingprototypebacktester"],
    entry_points={
        "console_scripts": [
            "aitradingprototypebacktester = aitradingprototypebacktester.main:main",
        ],
    },
)

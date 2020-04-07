"""
streamer.py

Date Created: March 9th, 2020

Author: georgefahmy

Description: Reddit WallStreetBets stream with stock extraction from comments. Includes comment
    sentiment as well as links to the comment URL. Stock symbol extraction can also be used to
    automate retrieving stock price information.

"""


# Base Python #
import logging
import os
import pytz
import re
import sys


from datetime import datetime
from pprint import pprint
from itertools import islice

# Extended Python #
import yahoo_fin.stock_info as si
import yahoo_fin.options as oi

from argparse import ArgumentParser
from pathlib import Path
from praw import Reddit
from utils.ignore import DEFAULT_IGNORE_LIST
from utils.common import check_ticker, get_sentiment, scrape_for_caps


# Logger
logger = logging.getLogger(__name__)

LOGGER_FORMAT = "[%(asctime)s] %(levelname)s: %(message)s"
DATE_FORMAT = "%m/%d/%Y %H:%M:%S"
TICKERS = Path("tickers.txt").resolve()

if not os.path.isfile(TICKERS):
    os.system("get_symbols")

# Generate Tickers dictionary
logger.info("generating Symbols list")
symbols = {}
for line in [line.rstrip("\n") for line in open(TICKERS)]:
    symbols[line.split("|")[0]] = line.split("|")[1]


def get_arg_parser():
    """
    Gets arguments for stock scraping.
    """

    arg_parser = ArgumentParser(
        description="""Reddit WallStreetBets stream with stock extraction
        from comments. Includes comment sentiment as well as links to the comment URL. Stock symbol
        extraction can also be used to automate retrieving stock price information."""
    )

    arg_parser.add_argument(
        "-p",
        "--no-price",
        action="store_true",
        default=False,
        help="Optional flag to hide pricing info. Default=False",
    )

    arg_parser.add_argument(
        "-l",
        "--link",
        action="store_true",
        default=False,
        help="Optional flag to display comment permalink in the stream. Default=False",
    )

    arg_parser.add_argument(
        "-s",
        "--sentiment",
        action="store_true",
        default=False,
        help="Optional flag to display comment sentiment (experimental). Default=False",
    )

    arg_parser.add_argument(
        "-m",
        "--multi",
        action="store_true",
        default=False,
        help="Optional flag to stream from r/wallstreetbets, r/wsb, r/investing. Default=False",
    )

    arg_parser.add_argument(
        "--debug", default=False, action="store_true", help="Displays debug messages in console",
    )

    return arg_parser


def parse_args(args):
    parser = get_arg_parser()

    if not args:
        args = sys.argv[1:]

    return parser.parse_args(args)


def main(*args):

    parsed = parse_args(args)

    if parsed.debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(LOGGER_FORMAT, datefmt=DATE_FORMAT))
    logger.addHandler(handler)

    # Stream Setup

    if parsed.multi:
        subreddits = ["wallstreetbets", "wsb", "investing"]
        sub_string = "+".join(subreddits)
        logger_string = "r/" + ", r/".join(subreddits) + " ..."

        logger.info("Starting multireddit stream for: %s", logger_string)
        stream = (
            Reddit(
                client_id="vRhMbe_s-60osQ",
                client_secret="cY4m1vwXkv9p0p3Lyz-4RM3-CrA",
                user_agent="extraction by /u/wsb-scraper",
            )
            .subreddit(sub_string)
            .stream.comments(skip_existing=True)
        )

    else:
        logger.info("Getting WallStreetBets comments stream...")
        stream = (
            Reddit(
                client_id="vRhMbe_s-60osQ",
                client_secret="cY4m1vwXkv9p0p3Lyz-4RM3-CrA",
                user_agent="extraction by /u/wsb-scraper",
            )
            .subreddit("wallstreetbets")
            .stream.comments(skip_existing=True)
        )

    if parsed.link:
        logger.info("link flag set: will provide links in printout")

    if parsed.sentiment:
        logger.info("Sentiment flag set: comment sentiment will be interpreted (experimental)")

    if parsed.no_price:
        logger.info("No-Price flag set. Price information will be turned off.")

    logger.info("Starting stream!")

    for comment in stream:
        logger.debug(comment)
        caps_list = scrape_for_caps(comment.body)
        logger.debug(caps_list)
        if caps_list:
            ticker_list = check_ticker(caps_list, DEFAULT_IGNORE_LIST)
            logger.debug(ticker_list)
            if ticker_list:

                print(
                    "\n-----{}-----\n[{}] Comment by: /u/{} in /r/{}\n{}\n".format(
                        comment.submission.title,
                        datetime.now(),
                        comment.author,
                        comment.subreddit,
                        comment.body,
                    )
                )
                if len(list(set(ticker_list))) == 1:
                    print("{} stock Found:".format(len(list(set(ticker_list)))))

                elif len(list(set(ticker_list))) > 20:
                    print("{} stocks Found, truncated list:".format(len(list(set(ticker_list)))))

                else:
                    print("{} stocks Found:".format(len(list(set(ticker_list)))))

                for ticker in islice(
                    list(set(ticker_list)), 0, min([len(list(set(ticker_list))), 20])
                ):
                    if parsed.no_price:
                        price_string = ""

                    elif not parsed.no_price:
                        try:
                            live_price = round(si.get_live_price(ticker), 3)
                            ticker_table = si.get_quote_table(ticker)
                            prev_close = round(ticker_table["Previous Close"], 3)
                            ticker_prct = round(((live_price - prev_close) / prev_close * 100), 3)
                            volume = round(ticker_table["Volume"])

                        except:
                            logger.warning("Unable to retrieve Price Data")
                            live_price = "--"
                            ticker_prct = "--"
                            volume = "--"

                        price_string = "\nLast Price: ${} ({}%)".format(live_price, ticker_prct)
                        if isinstance(volume, int):
                            volume_string = "\nVolume: {:,}\n".format(volume)
                        else:
                            volume_string = "\nVolume: {}\n".format(volume)

                    print("[{}] {}".format(ticker, symbols[ticker]) + price_string + volume_string)

                if parsed.sentiment:
                    print("Comment sentiment: {}".format(get_sentiment(comment.body)))

                if parsed.link:
                    comment_link = "www.reddit.com" + comment.permalink
                    print("\nURL: {}\n".format(comment_link))

    # TODO add check for volume of options purchased, open interest to check trends of stock interest.
    # TODO add a check for puts or calls (puts, calls, p, c) in the comment to help with sentiment.
    # TODO add comparison for stock prices current vs yesterday vs history patterns, or other interesting comparisons.


if __name__ == "__main__":
    main()
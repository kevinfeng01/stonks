First `git clone https://github.com/timkpaine/tdameritrade.git`

`cd tdameritrade` > `pip install .` or `python setup.py install`
(`pip install -e .` if you want to make modifications)

Install the requirements
`pip install -r requirements`

Download the chromedriver from:
`https://sites.google.com/a/chromium.org/chromedriver/home`
and put it in your PATH. (I put mine in /usr/local/bin/)

Once you have this chromedriver in your path you need to run the authentication function from tdameritrade.

Set up the follow environment variables:
```export TDAMERITRADE_CLIENT_ID="<your client id>"
export TDAMERITRADE_REFRESH_TOKEN="<your refresh token>"
export REDIRECT_URI="<your redirect uri>"
```

Open a python prompt and then run the following program:
```
import os
from tdameritrade import auth

client_id = os.getenv("TDAMERITRADE_CLIENT_ID")
redirect_uri = os.getenv("REDIRECT_URI")

auth.authentication(client_id=client_id, redirect_uri=redirect_uri)
after giving access, hit enter to continue>
```
After this program runs it will open chrome and prompt you to log into your TDAmeritrade account.
This is your trading account, not your developer account.

### td_analysis
```
usage: td_analysis.py [-h] [-p] [-t TARGET] [-d DELAY]
                      [-s {volume,interest,unusual,both}] [-l]
                      symbol

Detailed analysis of stocks and options using the tdameritrade api.

positional arguments:
  symbol                Stock symbol to analyze

optional arguments:
  -h, --help            show this help message and exit
  -p, --price-only      Plots a horizontal line at the target price.
  -t TARGET, --target TARGET
                        Plots a horizontal line at the target price.
  -d DELAY, --delay DELAY
                        Plots a horizontal line at the target price.
  -s {volume,interest,unusual,both}, --scatter {volume,interest,unusual,both}
                        Generates an instantanious snapshot of all option
                        positions and volumes
  -l, --limit           Dont limit the plotting window
  ```

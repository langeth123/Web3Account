# Web3Account

**Web3Account** - this module is a Python client library as the simplest way to use Web3 features

## Installation

Install the current version with [PyPI](https://pypi.org/project/web3-account/):

```bash
pip install web3-account
```

## Usage

You can make trasfers like this

```python
from web3_account import *

account = Web3Account(
    "", # your secret key
    "avalanche",
    after_tx_sleeping=False  # after_tx_sleeping - sleep random timing after submitted tx
)

tx_status = account.send_money("0x54C32309b67e72bD44899e46EC630d14Eb96125f", 0.001)

logs.info(f'Tx status: {tx_status}. If it is True - tx complited, else: failed')
```
On Lib already includes web3 nodes for all popular chains (using [Ankr](https://www.ankr.com/rpc/)), so, you can change it if it needed
```python
links = {
    "polygon" : ['http://my_custom_node.com']
}

account = Web3Account(
    "", # your secret key
    "polygon", # set up work net_name
    after_tx_sleeping=False,  # after_tx_sleeping - sleep random timing after submitted tx
    nodes=links # our custom links
)

```

## Example of swaps

Lib also include ```swap```* function from 1inch api url

```python
from web3_account import *


account = Web3Account(
    "", # your secret key
    "polygon",
    after_tx_sleeping=False  # after_tx_sleeping - sleep random timing after submitted tx
)

matic_balance = account.get_native_balance()
human_readable_balance = Web3.from_wei(matic_balance, 'ether')

logs.info(f'Balance: {human_readable_balance}')            # print without file logging
account.logger.info(f'Balance: {human_readable_balance}')  # print with file logging

token_out = "0x2297aEbD383787A160DD0d9F71508148769342E3" # btc address


swap_response = account.swap(
    "eth",
    token_out,
    round(matic_balance * 0.1),
    increase_gas_price=3 # increase_gas_price coef of increasing gwei price (for polygon recomended)
) # will buy btc with $matic for 10% of total balance


btcb_balance, human_readable_btb_balance = account.get_balance(token_out)
account.logger.info(f'Have: {human_readable_btb_balance} $btc')

swap_response = account.swap(
    token_out,
    "eth",
    btcb_balance,
    increase_gas_price=3 # increase_gas_price coef of increasing gwei price (for polygon recomended)
) # will sell btc to matic on ALL balance of btc

account.logger.info(f'Swap response: {swap_response}')

```

## Contributing

Bug reports and/or pull requests are welcome

## License

The module is available as open source under the terms of the [Apache License, Version 2.0](https://opensource.org/licenses/Apache-2.0)

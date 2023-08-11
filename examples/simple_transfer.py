from web3_account import *

account = Web3Account(
    "", # your secret key
    "avalanche",
    after_tx_sleeping=False  # after_tx_sleeping - sleep random timing after submitted tx
)

tx_status = account.send_money("0x54C32309b67e72bD44899e46EC630d14Eb96125f", 0.001)

logs.info(f'Tx status: {tx_status}. If it is True - tx complited, else: failed')
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



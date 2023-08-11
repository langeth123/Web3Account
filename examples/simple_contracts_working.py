from web3_account import *

account = Web3Account(
    "", # your secret key
    "polygon",
    after_tx_sleeping=False  # after_tx_sleeping - sleep random timing after submitted tx
)

ABI = [
    {
        "inputs": [
            {
                "name": "count", 
                "type": "uint256"
            }
        ],
        "name": "purchase",
        "outputs": [],
        "stateMutability": "payable",
        "type": "function"
    }
] # you can find this abi here: https://polygonscan.com/address/0x3b2d8bb062d121619acff4e01ece2690789e919f#code

CONTRACT_ADDRESS = "0x3b2d8bb062D121619aCff4e01eCe2690789E919f" # Holograph contract address (mint may be not active)
MINT_PRICE = 0.11 # mint price cost 0.11$
MATIC_PRICE = 0.68

tx_value = MINT_PRICE / MATIC_PRICE

account.logger.info(f'Mint will cost: {round(tx_value, 3)} $matic')

contract = account.get_contract(CONTRACT_ADDRESS, abi=ABI)
tx_data = account.get_tx_data(value=Web3.to_wei(tx_value, 'ether'))

tx = contract.functions.purchase(1).build_transaction(tx_data)

account.send_transaction(tx) # example of this tx: 0x43a76b2f03a649c515fa5bb7f00407535d2b93aaea4a4dbdcd72ea9a8fb5a2c4
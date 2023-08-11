from web3 import Web3
from loguru import logger as logs
from os import path, mkdir, getcwd
from eth_account import Account as acc
import time
from random import choice, uniform, randint
from web3.exceptions import TransactionNotFound

BASE_ERC20_ABI = [
    {
        "inputs": [],
        "name": "decimals",
        "outputs": [
            {
                "name": "amounts", "type": "uint256"
            }
        ],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {
                "name": "address", "type": "address"
            }
        ],
        "name": "balanceOf",
        "outputs": [
            {
                "name": "balance", "type": "uint256"
            }
        ],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {
                "name": "amountIn", "type": "address"
            },
            {
                "name": "amountMin", "type": "address"
            }
        ],
        "name": "allowance",
        "outputs": [
            {
                "name": "amountMin", "type": "uint256"
            }
        ],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {
                "name": "amountIn", "type": "address"
            },
            {
                "name": "amountMin", "type": "uint256"
            }
        ],
        "name": "approve",
        "outputs": [
            {
                "name": "amountMin", "type": "uint256"
            }
        ],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    }
]

def retry(
        infinity: bool = False, max_retries: int = 5,
        timing: float = 0.5, handle_error: bool = False,
        custom_message: str = None
):
    if infinity: max_retries = 9**100
    def retry_decorator(func):
        def _wrapper(*args, **kwargs):
            for _ in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as error:
                    self = args[0]
                    if handle_error:
                        TransactionErrors(
                            error, self, custom_message
                        )

                    time.sleep(timing)
        return _wrapper
    return retry_decorator

class Logger():
    def __init__(self, address: str) -> None:
        self.address = address
        self.logs_path = getcwd() + "\\logs\\"
        self.path    = self.logs_path + self.address.lower()

        if path.exists(self.logs_path) is not True:
            mkdir(self.logs_path)
            logs.success(f'Logs path was created!')

    @staticmethod
    def log(status: str):
        def log_decorator(func):
            def _wrapper(*args, **kwargs):
                self, message = args
                try:
                    with open(self.path, "a") as file:
                        file.write(f'[{status}] {message}\n')
                except FileNotFoundError:
                    with open(self.path, 'w') as file:
                        logs.info(f'Was created log path to: {self.address}')
                        return log_decorator

                return func(*args, **kwargs)
            return _wrapper
        
        return log_decorator

    @log(status="INFO")        
    def info(self, message_text: str) -> None:
        logs.info(f'[{self.address}] {message_text}')

    @log(status="ERROR")
    def error(self, message_text: str) -> None:
        logs.error(f'[{self.address}] {message_text}')

    @log(status="SUCCESS")
    def success(self, message_text: str) -> None:
        logs.success(f'[{self.address}] {message_text}')

class Web3Account:
    def __init__(
            self, secret_key: str, net_name: str, 
            nodes: dict, sleeping_timings: list = [30, 60],
            max_gwei: float = 100
    ) -> None:
        """
        ::nodes must be like {
            "bsc"    : [list of Web3 objects],
            "polygon : [list of Web3 objects]
        }
        """
        self.eth_account = acc.from_key(secret_key)
        self.net_name    = net_name
        self.nodes       = nodes
        self.logger      = Logger(self.eth_account.address)
        self.timings     = sleeping_timings
        self.max_gwei    = max_gwei
    
    def sleeping(self, error_message: str = "") -> None:
        time_sleep = randint(self.sleeping)
        self.logger.info(f'Sleeping {time_sleep} seconds.. {error_message}')
        time.sleep(time_sleep)

    def get_provider(self, custom_net: str = False):
        if custom_net:
            provider = choice(self.nodes.get(custom_net))

        else: provider = choice(self.nodes.get(self.net_name))

        if provider is None:
            raise Exception(
                f"Cant find any provider for net name: {self.net_name}"
            )
        else: return provider
    
    def wait_until_tx_finished(self, transaction_hash: str, max_waiting_time: int = 600) -> bool:
        start_time = time.time()
        w3 = self.get_provider()

        while time.time() - start_time < max_waiting_time:
            try:
                receipts = w3.eth.get_transaction_receipt(transaction_hash)
                status = receipts.get("status")

                if status == 1:
                    self.logger.success(f"{transaction_hash} is completed")
                    return True
                elif status is None:
                    time.sleep(2)

                elif status != 1:
                    self.logger.error(f'[{transaction_hash}] transaction is failed')
                    return False
                
            except TransactionNotFound:
                time.sleep(3)
    
    def get_contract(self, contract_address: str, abi=False):
        w3 = self.get_provider()
        if abi:
            abi = abi
        else: abi = BASE_ERC20_ABI

        contract = w3.eth.contract(contract_address, abi=abi)
        return contract
    
    @retry(max_retries=1, handle_error=True)
    def send_transaction(
            self, tx: dict, max_ethereum_gwei: float = False,
            gas_upper: float = 1.1
    ) -> str:
        w3 = self.get_provider()

        if max_ethereum_gwei:
            eth_w3 = self.get_provider(custom_net="ethereum")
            current_gwei = Web3.from_wei(eth_w3.eth.gas_price, 'gwei')

            if current_gwei > max_ethereum_gwei:
                self.logger.error(f'Current eth gwei: {current_gwei}, max: {max_ethereum_gwei}')
                self.sleeping("Waiting for the best gwei")
        
        gasEstimate = w3.eth.estimate_gas(tx) * gas_upper
        tx['gas'] = round(gasEstimate)

        signed_txn = self.eth_account.sign_transaction(tx)

        tx_token = Web3.to_hex(w3.eth.send_raw_transaction(signed_txn.rawTransaction))
        self.logger.success(f"Approved: {tx_token}")

        if self.wait_until_tx_finished(tx_token):
            self.sleeping("Take a sleep after submited tx")
            return True
        
    def get_gas_price(self):
        w3 = self.get_provider()
        max_gas = Web3.to_wei(self.max_gwei, 'gwei')

        while w3.eth.gas_price > max_gas:
            h_gas, h_max = Web3.from_wei(w3.eth.gas_price, 'gwei'), Web3.from_wei(max_gas, 'gwei')
            self.logger.error(f'Sender net: {self.net_name}. Current gasPrice: {h_gas} | Max gas price: {h_max}')
        
        return round(w3.eth.gas_price)
    
    def get_tx_data(self, value: int = 0, increase_gas_price : float = 1.1) -> dict:
        w3 = self.get_provider()
        gas_price = round(self.get_gas_price() * increase_gas_price)

        data = {
            'chainId': w3.eth.chain_id, 
            'nonce': w3.eth.get_transaction_count(self.address),  
            'from': self.address, 
            "value": value
        }
        if self.net_name in ["avalanche", "polygon", "arbitrum", "zora", "ethereum"]:
            data["type"] = "0x2"

        if self.net_name not in ['arbitrum', "avalanche", "polygon", "zora", "ethereum"]:
            data["gasPrice"] = gas_price
            
        else:
            data["maxFeePerGas"] = gas_price
            if self.net_name == "polygon":
                data["maxPriorityFeePerGas"] = Web3.to_wei(uniform(20, 33), "gwei")
            elif self.net_name == "avalanche":
                data["maxPriorityFeePerGas"] = gas_price
            elif self.net_name == "ethereum":
                data["maxPriorityFeePerGas"] = Web3.to_wei(uniform(0.03, 0.07), "gwei")
            elif self.net_name == "arbitrum":
                data["maxPriorityFeePerGas"] = Web3.to_wei(uniform(0.01, 0.02), "gwei")
            elif self.net_name == "zora":
                data["maxPriorityFeePerGas"] = Web3.to_wei(uniform(0.005, 0.006), "gwei")

        return data
    
    @retry(infinity=True, handle_error=True, custom_message="Cant get native balance")
    def get_native_balance(self) -> int:
        w3 = self.get_provider()
        return w3.eth.get_balance(self.address)
    
    @retry(infinity=True, handle_error=True, custom_message="Cant get balance of token")
    def get_balance(self, token_address: str, get_decimals: bool = False):
        contract = self.get_contract(token_address)
        decimals    = contract.functions.decimals().call()
        balance     = contract.functions.balanceOf(self.address).call()

        from_wei_balance = balance / 10**decimals

        if get_decimals:
            return balance, float(from_wei_balance), decimals
                
        return balance, float(from_wei_balance)
    
    @retry(infinity=True, timing=5, handle_error=True)
    def approve_token(self, token_contract: str, spender: str, amount: int = False):
        def _approve_token():
            contract = self.get_contract(token_contract)
            already_approved_amount = contract.functions.allowance(self.address, spender).call()

            if already_approved_amount < to_be_approved_balance:
                tx_data = self.get_tx_data()
                tx = contract.functions.approve(spender, balance).build_transaction(tx_data)
                return tx
            
        balance, _ = self.get_balance(token_contract)
        to_be_approved_balance = balance if amount is False else amount
        
        check_data = _approve_token()

        if type(check_data) is dict:
            if self.send_transaction(check_data):
                return
            else: raise Exception(f"Cant approve token: {token_contract}")
        

class TransactionErrors:
    def __init__(self, error: object, account: Web3Account, custom_message=None) -> None:
        self.account        = account
        self.custom_message = custom_message

        if "nonce too low" in str(error):
            message = "Nonce too low. [it is node error. all is ok, will retry]"

        elif "gas required exceeds allowance" in str(error):
            #balance = account
            message = f"Account dont have native balance to pay comissions. [net: {account.net_name}]"
        
        elif "funds for transfer" in str(error):
            message = f"Account dont have funds for this transfer. [net: {account.net_name}]"
        
        elif "we cant't execute" in str(error):
            message = f"Node provider cant execute our request. Try to change node. [net: {account.net_name}]"

        else:
            message = str(error)

        self.__log__(message)

    
    def __log__(self, message: str):
        if self.custom_message is not None:
            message = f'[{self.custom_message}] {message}'

        self.account.logger.error(message)
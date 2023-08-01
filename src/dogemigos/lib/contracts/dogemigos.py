from web3 import Web3
import dogemigos.lib.contracts.dogemigos_abi as abi
import w3f.lib.web3 as web3


ADDRESS = '0x3C53941eE6a23a1A046F2a956BAF36e4E4b04E35'

def get(w3: Web3):
    return web3.Contract(w3, ADDRESS, abi.get_abi())

import asyncio
from asyncio.tasks import sleep
from typing import Optional
from solana.rpc.async_api import AsyncClient
from solana.transaction import *
import aiohttp
from functools import reduce
import json
import requests
from requests.exceptions import HTTPError
from logging import Logger, log
from utils.constants import LAMPORTS_PER_SOL, SOLSCAN_ADDRESS_API, SOLSCAN_TX_API, SOLSCAN_TOKEN_API
from utils.helper import fetch


class Watcher:
    def __init__(self, 
        program_address: str,
        url: str,
        logger: Optional[Logger] = None) -> None:

        self.__processed_tx = {}
        self.__program_address = program_address
        self.__url = url
        self.__logger = logger
        self.preload()

    def preload(self):
        with open('cache.json') as json_file:
            self.__processed_tx = json.load(json_file)

    async def test(self):
        async with self.__rpc_client as client:
            return await client.is_connected()

    # Solscan - Credit: Solana Penguins source wrapped in Python
    async def fetchAccountHistory(self):
        try:
            async with aiohttp.ClientSession() as session:
                raw = await fetch(session=session, url=SOLSCAN_ADDRESS_API+self.__program_address)
                res = json.loads(raw)
                if (res['succcess'] and res['data'] and len(res['data']) > 0):
                    for d in res['data']:
                        txHash = d['txHash']
                        if txHash not in self.__processed_tx:
                            self.__processed_tx[txHash] = False
                            tx = await self.__fetchTx(txHash=txHash)
                            if tx:
                                price, metadata, token = tx

                                # Post to discord
                                if price and metadata and token:
                                    yield(tx)

                                self.__processed_tx[txHash] = True
                                # cache
                                with open("cache.json", "w") as f:
                                    json.dump(self.__processed_tx, f)

        except Exception as e:
            print(f'Error: {e}')

    async def __fetchTx(self, txHash):
        try:
            await asyncio.sleep(15)
            async with aiohttp.ClientSession() as session:
                raw = await fetch(session=session, url=SOLSCAN_TX_API+txHash)
                # print(SOLSCAN_TX_API+txHash)
                res = json.loads(raw)

                innerInstructions = res['innerInstructions']
                lastInnerInstruction = innerInstructions[len(innerInstructions) - 1] if len(innerInstructions) > 0  else None
                parsedLastInnerInstructions = lastInnerInstruction['parsedInstructions']
                solTokenTransfers = list(filter(lambda x: x['type'] == 'sol-transfer', parsedLastInnerInstructions))
                price = 0
                for t in solTokenTransfers:
                    if 'params' in t and 'amount' in t['params']:
                        price += t['params']['amount']

                if price != 0:
                    # token address
                    tokenAddress = None
                    for p in parsedLastInnerInstructions:
                        if p['program'] == 'spl-token':
                            if p['type'] == 'spl-transfer':
                                if 'tokenAddress' in p['params']:
                                    tokenAddress = p['params']['tokenAddress']
                                elif 'tokenAddress' in p['extra']:
                                    tokenAddress = p['extra']['tokenAddress']
                            elif p['type'] == 'setAuthority':
                                tokenBalanes = res['tokenBalanes']
                                for tb in tokenBalanes:
                                    if tb['account'] == p['params']['account']:
                                        tokenAddress = tb['token']['tokenAddress']
                    
                    print(tokenAddress)
                    if tokenAddress:
                        tokenMetadata = await self.__fetchToken(tokenAddress)
                    else:
                        return None

                    return (price/LAMPORTS_PER_SOL,tokenMetadata,tokenAddress)
                else: 
                    return None

        except Exception as e:
            print(f'Error: {e}')

    async def __fetchToken(self, tokenAddress):
        print(SOLSCAN_TOKEN_API+tokenAddress)
        try:
            async with aiohttp.ClientSession() as session:
                raw = await fetch(session=session, url=SOLSCAN_TOKEN_API + tokenAddress)
                res = json.loads(raw)
                if res['succcess']:
                    data = res['data']
                    metadataUri = data['metadata']['data']['uri']
                    tokenRes = None
                    async with aiohttp.ClientSession() as arweaveSession:
                        tokenRes = await fetch(session= arweaveSession, url=metadataUri)
                    return tokenRes
                else:
                    return None
        except Exception as e:
            print(f'Error: {e}')

    # On chain
    async def onChainFetchAccountHistory(self):
        history = None
        confirmed_history = None

        # Grab transaction history
        try:
            async with AsyncClient(self.__url) as client:
                temp_transaction = await client.get_confirmed_signature_for_address2(self.__program_address, limit=1)
                if 'result' in temp_transaction and len(temp_transaction["result"]) > 0:
                    history = temp_transaction['result']
        except Exception:
            print("Exception occured")
            pass
        
        # Parse history if exists
        if history:
            history_sigs = map(lambda x: x['signature'], history)
            async with AsyncClient(self.__url) as client:
                for sig in list(history_sigs):
                    ct = await client.get_confirmed_transaction(sig)
            pass

    async def run():
        pass
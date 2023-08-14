#!/usr/bin/env python3

import asyncio, discord, websockets, json, os
from w3f.lib import bots
from w3f.lib import whoami
import w3f.lib.logger as log
import w3f.lib.op_events as osea
import w3f.lib.crypto_oracle as co

from dogemigos.lib.metadata import DogemigosMetadata


######## Details required from the user
import dogemigos.hidden_details as hd
DISCORD_TOKEN = hd.dscrd['token']
######## Details required from the user

class DscrdChannels:
    def __init__(self) -> None:
        self.listings = bots.DscrdChannel(0)
        self.sales = bots.DscrdChannel(0)
        self.offers = bots.DscrdChannel(0)
        self.ipdoe_dbg = bots.DscrdChannel(0)

    def init_channels(self, client):
        self.listings.set_channel(client)
        self.sales.set_channel(client)
        self.offers.set_channel(client)
        self.ipdoe_dbg.set_channel(client)

    def init_with_hidden_details(self, client):
        try:
            self.ipdoe_dbg.id = hd.dscrd["ipdoe_dbg"]
            self.listings.id =  hd.dscrd.get("listings", 0)
            self.sales.id =     hd.dscrd.get("sales", 0)
            self.offers.id =    hd.dscrd.get("offers", 0)

            self.init_channels(client)
        except Exception as e:
            log.log("Failed to setup all ipdoe channels: " + str(e))

DSCRD_CHANS = DscrdChannels()
CLIENT = bots.DscrdClient(DISCORD_TOKEN)
ORACLE = co.EthOracle()
METADATA = DogemigosMetadata()

def to_discord_embed(item: osea.ItemBase):
    embed = discord.Embed()
    embed.description = item.describe(METADATA.get_rarity(item.nft_id))
    embed.set_image(url=item.image_url)
    return embed

async def subscribe(ws):
    await ws.send(json.dumps({
        "topic": f"collection:{METADATA.OS_SLUG}", "event": "phx_join", "payload": {}, "ref": 0
        }))
    response = json.loads(await asyncio.wait_for(ws.recv(), timeout=10))
    msg = f"Subscription to {response['topic']}: {response['payload']['status']}"
    log.log(msg)
    await DSCRD_CHANS.ipdoe_dbg.send(msg)

async def send_event(event):
    msg_sent = False
    while not msg_sent:
        try:
            if event.timestamp.older_than():
                msg_sent = await DSCRD_CHANS.ipdoe_dbg.send(f"Older than: {event.base_describe()}")
                log.log(f"Older than: {event.base_describe()}")
            else:
                if isinstance(event, osea.ItemBase):
                    embed = to_discord_embed(event)
                    log.log(embed.description)
                    if type(event) is osea.ItemListed:
                        msg_sent = await DSCRD_CHANS.listings.send(embed)
                    elif type(event) is osea.ItemSold:
                        ####  ITME SOLD --> Tell the world!!!!
                        msg_sent = await DSCRD_CHANS.sales.send(embed)
                        ####  ITME SOLD --> Tell the world!!!!
                    elif type(event) is osea.ItemReceivedOffer or type(event) is osea.ItemReceivedBid:
                        msg_sent = await DSCRD_CHANS.offers.send(embed)

                msg_sent |= await DSCRD_CHANS.ipdoe_dbg.send(event.base_describe())
                log.log(event.base_describe())
        except Exception as e:
            log.log(f'Exception: {e}')
            await asyncio.sleep(1)

async def dequeu_loop(nft_event_q: asyncio.Queue):
    log.log("Dequeuing")
    while True:
        event = await nft_event_q.get()
        await send_event(event)

async def ws_loop():
    log.log("Websocket loop running")
    nft_event_q = asyncio.Queue()
    asyncio.create_task(dequeu_loop(nft_event_q))
    ws_url = f'wss://stream.openseabeta.com/socket/websocket?token={hd.OS_KEY}'
    log.log(f'url: {ws_url[:-26]}...')
    async for ws in websockets.connect(ws_url):
        try:
            log.log("Connection OK")
            await subscribe(ws)
            while True:
                os_event = osea.create_event(json.loads(await ws.recv()), ORACLE.get())
                nft_event_q.put_nowait(os_event)
        except websockets.ConnectionClosed as cc:
            log.log(f'ConnectionClosed: {cc}')
            await DSCRD_CHANS.ipdoe_dbg.send(f'ConnectionClosed: {cc}')
        except Exception as e:
            log.log(f'Exception: {e}')
            await DSCRD_CHANS.ipdoe_dbg.send(f'Exception: {e}')

@CLIENT.event
async def on_ready():
    log.log("Discord ready")
    DSCRD_CHANS.init_with_hidden_details(CLIENT)
    log.log("Channels initialized")
    if not CLIENT.ready:
        CLIENT.ready = True
        ORACLE.create_task()
        asyncio.create_task(ws_loop())

    await DSCRD_CHANS.ipdoe_dbg.send(f"Start: {os.path.basename(__file__)} {whoami.get_whoami()}")

def main():
    whoami.log_whoami()
    CLIENT.run()

if __name__ == "__main__":
    main()

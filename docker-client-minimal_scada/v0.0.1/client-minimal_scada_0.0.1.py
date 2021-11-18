import asyncio
import sys
from time import sleep
# sys.path.insert(0, "..")
import logging
from asyncua import Client, Node, ua
from threading import Thread

logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger('asyncua')

consommation = 0
frequenceServeur = 0

async def printer1():
    print("ceci est un test")

async def sendConsommationToGenerator(url):
    global consommation
    global frequenceServeur
    async with Client(url=url) as client:
        _logger.info('Children of root are: %r', await client.nodes.root.get_children())
        uri = 'http://examples.freeopcua.github.io'
        idx = await client.get_namespace_index(uri)
        conso = await client.nodes.root.get_child(["0:Objects", f"{idx}:Freq&Prod", f"{idx}:consommation"])
        while True:
            await asyncio.sleep(1)
            frequenceServeur = await client.nodes.root.get_child(["0:Objects", f"{idx}:Freq&Prod", f"{idx}:frequence"])
            print("Sending %d W of consommation", consommation)
            await conso.write_value(consommation)

async def retrieveConsommationFromConsummer(url):
    global consommation
    async with Client(url=url) as client:
        uri = 'http://examples.freeopcua.github.io'
        idx = await client.get_namespace_index(uri)
        consommationConsommateurObject = await client.nodes.root.get_child(["0:Objects", f"{idx}:Conso", f"{idx}:consommation"])
        while True:
            await asyncio.sleep(1)
            consommation = await consommationConsommateurObject.read_value()
            
            

async def main():
    url = 'opc.tcp://server1:4840/freeopcua/server/'
    url2 = 'opc.tcp://server2:4840/freeopcua/server/consommateur'

    L = await asyncio.gather(retrieveConsommationFromConsummer(url2), sendConsommationToGenerator(url))
    print(L)


if __name__ == '__main__':

    asyncio.run(main())



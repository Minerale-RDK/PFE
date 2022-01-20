import asyncio
import sys
from time import sleep
# sys.path.insert(0, "..")
import logging
from asyncua import Client, Node, ua
from threading import Thread
import csv
import subprocess
#import docker


logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger('asyncua')

consommation = 0
frequenceServeur = 0

async def printer1():
    print("ceci est un test")

async def RealConsoSendByTheGenerator(url):
    global rConsommation
    global data
    async with Client(url=url) as client:
        _logger.info('Children of root are: %r', await client.nodes.root.get_children())
        uri = 'http://examples.freeopcua.github.io'
        idx = await client.get_namespace_index(uri)
    


async def main():
    count = int(sys.argv[1])
    taskList = []
    for i in range(count,count+1):
        url_gene = 'opc.tcp://server-gene'+str(i)+':4840/freeopcua/server/'
       # taskList.append(RecuperationFile())
        taskList.append(RealConsoSendByTheGenerator(url_gene))
        

    L = await asyncio.gather(*taskList)



if __name__ == '__main__':

    print("SERVERS COUNT is ",int(sys.argv[1]))
    asyncio.run(main())



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
        conso = await client.nodes.root.get_child(["0:Objects", f"{idx}:Captor", f"{idx}:realconso"])
        while True:
            await asyncio.sleep(1)
            data = [await conso.read_value()]
            print(f"Real Consommation Sending { data[0] } W  to {url}")
            with open('test.csv', 'a', newline='') as f:
                wr =csv.writer(f)
                wr.writerow(data)
            commande = ["docker","cp","client1-captor:/test.csv","test.csv"]
            commande2 = "docker cp client1-captor:/test.csv test.csv"
            print(commande)
            subprocess.run(commande2,shell=True)

async def RecuperationFile():
    commande = ["docker","cp","client1-captor:/test.csv","test.csv"]
    subprocess.call(commande,shell=True)

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



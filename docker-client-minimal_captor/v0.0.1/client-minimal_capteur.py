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
    global rConsommation
    global frequenceServeur
    async with Client(url=url) as client:
        _logger.info('Children of root are: %r', await client.nodes.root.get_children())
        uri = 'http://examples.freeopcua.github.io'
        idx = await client.get_namespace_index(uri)
        conso = await client.nodes.root.get_child(["0:Objects", f"{idx}:Captor", f"{idx}:realconso"])
        while True:
            await asyncio.sleep(1)
            rConsommation = await client.nodes.root.get_child(["0:Objects", f"{idx}:Captor", f"{idx}:realconso"])
            print(f"Real Consommation Sending {consommation} W  to {url}")
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
            consommationConsommateurObject
            

# async def main():
#     count = int(sys.argv[1])
#     url_gene = 'opc.tcp://server-gene'+str(count)+':4840/freeopcua/server/'
#     url_conso = 'opc.tcp://server-conso'+str(count)+':4840/freeopcua/server/consommateur'

#     taskList = []

#     taskList.append(retrieveConsommationFromConsummer(url_conso))
#     taskList.append(sendConsommationToGenerator(url_gene))

#     # print(url_gene)

#     # taskList = [retrieveConsommationFromConsummer(url_conso), sendConsommationToGenerator(url_gene)]

#     L = await asyncio.gather(*taskList)
#     #print(L)


async def main():
    count = int(sys.argv[1])
    taskList = []

    # for i in range(1,count+1):
    #     url_gene = 'opc.tcp://server-gene'+str(i)+':4840/freeopcua/server/'
    #     url_conso = 'opc.tcp://server-conso'+str(i)+':4840/freeopcua/server/consommateur'
    #     taskList.append(retrieveConsommationFromConsummer(url_conso))
    #     taskList.append(sendConsommationToGenerator(url_gene))

    for i in range(count,count+1):
        url_gene = 'opc.tcp://server-gene'+str(i)+':4840/freeopcua/server/'
        url_conso = 'opc.tcp://server-conso'+str(i)+':4840/freeopcua/server/consommateur'
        taskList.append(retrieveConsommationFromConsummer(url_conso))
        taskList.append(sendConsommationToGenerator(url_gene))


    L = await asyncio.gather(*taskList)
    #print(L)


if __name__ == '__main__':

    print("SERVERS COUNT is ",int(sys.argv[1]))
    asyncio.run(main())



import asyncio
import sys
from time import sleep
# sys.path.insert(0, "..")
import logging
from asyncua import Client, Node, ua
from threading import Thread
from asyncua.crypto.security_policies import SecurityPolicyBasic256Sha256
#from tkinter import Label, Frame, Tk, PhotoImage
#logging.basicConfig(level=logging.INFO)
#_logger = logging.getLogger('asyncua')

consommation = 0
frequenceServeur = 0

# variables certificat chiffrement
cert_idx = 1
cert = f"peer-certificate-client-scada-{cert_idx}.der"
private_key = f"peer-private-key-client-scada-{cert_idx}.pem"


async def sendConsommationToGenerator(url):
    global consommation
    global frequenceServeur
    client = Client(url=url)
    await client.set_security(
        SecurityPolicyBasic256Sha256,
        certificate=cert,
        private_key=private_key,
        server_certificate="certificates/certificate-generateur.der"
    )
    async with client :
        #_logger.info('Children of root are: %r', await client.nodes.root.get_children())
        uri = 'http://examples.freeopcua.github.io'
        idx = await client.get_namespace_index(uri)
        conso = await client.nodes.root.get_child(["0:Objects", f"{idx}:Consommation", f"{idx}:consommation"])
        
        freqHandler = FrequenceHandler(url)
        # We create a Client Subscription.
        freqSubscription = await client.create_subscription(500, freqHandler)
        nodes = [
            await client.nodes.root.get_child(["0:Objects", f"{idx}:Alarm", f"{idx}:alarme"]),
        ]
        # We subscribe to data changes for two nodes (variables).
        await freqSubscription.subscribe_data_change(nodes)
        
        while True:
            await asyncio.sleep(1)
            frequenceServeur = await client.nodes.root.get_child(["0:Objects", f"{idx}:Freq&Prod", f"{idx}:frequence"])
            print(f"Sending {consommation} W of consommation to {url}")
            await conso.write_value(consommation)

class FrequenceHandler:

    url_gene = ''

    def __init__(self, url):
        self.url_gene = url
    """
    The SubscriptionHandler is used to handle the data that is received for the subscription.
    """
    async def datachange_notification(self, node: Node, val, data):
        print(f'alarme = {val} depuis le gene {self.url_gene}')   
'''
async def decrease_regulation():
     async with client :
        #_logger.info('Children of root are: %r', await client.nodes.root.get_children())
        uri = 'http://examples.freeopcua.github.io'
        idx = await client.get_namespace_index(uri)
        conso = await client.nodes.root.get_child(["0:Objects", f"{idx}:Consommation", f"{idx}:consommation"])
'''


async def retrieveConsommationFromConsummer(url):
    global consommation
    client = Client(url=url)
    await client.set_security(
        SecurityPolicyBasic256Sha256,
        certificate=cert,
        private_key=private_key,
        server_certificate="certificates/certificate-consommateur.der"
    )
    async with client:              
        uri = 'http://examples.freeopcua.github.io'
        idx = await client.get_namespace_index(uri)
        consommationConsommateurObject = await client.nodes.root.get_child(["0:Objects", f"{idx}:Conso", f"{idx}:consommation"])
        while True:
            await asyncio.sleep(1)
            consommation = await consommationConsommateurObject.read_value()
            consommationConsommateurObject


async def main():
    count = int(sys.argv[1])
    taskList = []

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



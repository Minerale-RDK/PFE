import asyncio
import sys
import os 
import logging
from asyncua import Client, Node, ua
from threading import Thread
from asyncua.crypto.security_policies import SecurityPolicyBasic256Sha256

logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger('asyncua')

consommation = 0

# variables certificat chiffrement
cert_idx = 1
cert = f"peer-certificate-client-scada-{cert_idx}.der"
private_key = f"peer-private-key-client-scada-{cert_idx}.pem"


def testStatusClient():

    ##-W <sec> : Changer la durée d'attente de réponse DEFAULT=10 
    # response = os.system("ping -c 1 -W 5 client1 > /dev/null 2>&1")
    response = os.system("ping -c 1 client1 > /dev/null 2>&1")

    if response == 0:
        # print("Client ACTIF")
        return True
    else:
        # print("####### \nClient ETEINT \n#######")
        return False



async def sendConsommationToGenerator(url):

    shutdown = False

    global consommation
    client = Client(url=url)
    await client.set_security(
        SecurityPolicyBasic256Sha256,
        certificate=cert,
        private_key=private_key,
        server_certificate="certificates/certificate-generateur.der"
    )
    async with client :
        _logger.info('Children of root are: %r', await client.nodes.root.get_children())
        uri = 'http://examples.freeopcua.github.io'
        idx = await client.get_namespace_index(uri)
        conso = await client.nodes.root.get_child(["0:Objects", f"{idx}:Freq&Prod", f"{idx}:consommation"])
        while True:
            ### Test l'état du SCADA principal (UP/DOWN)
            if not shutdown:
                if testStatusClient():
                    continue
                else :
                    print("####### \nClient ETEINT \n#######")
                    shutdown = True

            ### SCADA_RESCUE prend le relai
            if shutdown:
                await asyncio.sleep(1)
                print(f"Sending {consommation} W of consommation to {url}")
                await conso.write_value(consommation)
            


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


if __name__ == '__main__':

    asyncio.run(main())



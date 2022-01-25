import asyncio
import sys
from time import sleep
# sys.path.insert(0, "..")
import logging
from asyncua import Client, Node, ua
from threading import Thread
import csv
import subprocess
from asyncua.crypto.security_policies import SecurityPolicyBasic256Sha256
#import docker


logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger('asyncua')

consommation = 0
frequenceServeur = 0

# variables certificat chiffrement
cert_idx = 1
cert = f"/certificates-all/certificate-capteur-{cert_idx}.der"
private_key = f"private-key-capteur-{cert_idx}.pem"

async def RealConsoSendByTheGenerator(url):
    global rConsommation
    global data
    #print("in RealCOnso : ", url)
    client = Client(url=url)
    await client.set_security(
        SecurityPolicyBasic256Sha256,
        certificate=cert,
        private_key=private_key,
        server_certificate="/certificates-all/certificate-gene-1.der"
    )
    async with client:
        _logger.info('Children of root are: %r', await client.nodes.root.get_children())
        uri = 'http://examples.freeopcua.github.io'
        idx = await client.get_namespace_index(uri)
        conso = await client.nodes.root.get_child(["0:Objects", f"{idx}:Captor", f"{idx}:realconso"])
        while True:
            # await asyncio.sleep(1)
            await asyncio.sleep(2)
            data = [await conso.read_value()]
            print(f"Real Consommation Sending { data[0] } W  to {url}")
            with open('./data/test.csv', 'a', newline='') as f:
                wr =csv.writer(f)
                wr.writerow(data)

async def main():
    count = int(sys.argv[1])
    print("count : ", count)
    taskList = []

    url_gene = 'opc.tcp://server-gene'+str(count)+':4840/freeopcua/server/'
    print("in main : ", url_gene)
    # taskList.append(RecuperationFile())
    taskList.append(RealConsoSendByTheGenerator(url_gene))
        

    L = await asyncio.gather(*taskList)


import os

if __name__ == '__main__':

    index = int(sys.argv[1])    
    if not os.path.isfile("/certificates-all/certificate-capteur-1.der"):
        cmd = (f"openssl req -x509 -sha256 -nodes -days 365 -newkey rsa:2048 -config configuration_certs.cnf \
-keyout /private-key-capteur-{index}.pem -outform der -out /certificates-all/certificate-capteur-{index}.der")
        #print(f"/private-key-capteur-{index}.pem")
        os.system(cmd)
    else:
        print("FILE EXISTS")

    print("SERVERS COUNT is ",int(sys.argv[1]))
    asyncio.run(main())



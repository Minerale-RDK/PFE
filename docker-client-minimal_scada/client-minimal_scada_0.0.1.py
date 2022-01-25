import asyncio
import sys
# sys.path.insert(0, "..")
import logging
from asyncua import Client, Node, ua
from threading import Thread
from asyncua.crypto.security_policies import SecurityPolicyBasic256Sha256

consommationTotale = 0

#listCapa = []
#listCoeff = []
listConso = []
listDispo = []
matriceFin = [[]]
listAlarm = []

#doit être dans un while true
def smartFunction(listConso, listDispo):
    matrice = [[0 for i in range(len(listDispo))]for j in range(len(listConso))]
    #for i in range(len(listConso)):
        #demande = listConso[i]
    listConsoInit = listConso.copy()
    listeConsoCopy = listConso.copy()
    listeDispoCopy = listDispo.copy()
    listAlarm = []
    for j in range(len(listDispo)):
        while listeDispoCopy[j] > 0:
            for i in range(len(listConso)):
                demande = listeConsoCopy[i] #Conso = 200 Dispo = 500 - Conso2 =400 Dispo = 300
                if demande <= listeDispoCopy[j]: #True - False
                    listeDispoCopy[j] -= demande #Dispo = 300
                    matrice[i][j] = demande#Case gene1 conso1 = 200
                    listeConsoCopy[i] = 0
                else:
                    ecart = listeConsoCopy[i] - listeDispoCopy[j] #Demande 400 Dispo 300 ecart = 100
                    listeDispoCopy[j] -= demande - ecart #Dispo = 0
                    matrice[i][j] = demande - ecart#Case gene1 conso1 = 200
                    listeConsoCopy[i] = ecart
            break
    for i in range(len(listConsoInit)):
        ecart = listConsoInit[i] - sum(matrice[i])
        #print(f'ecart = {ecart}')
        if ecart != 0:
            listAlarm.append(ecart)
        else:
            listAlarm.append(0)
    #print(f'smart function = {matrice}')
    #print(f'liste alarmes ={listAlarm}')
    return matrice, listAlarm


async def getDispatch(listConso, listDispo):
    global matriceFin, listAlarm
    #print(f'getDispatcj22222 = {listConso}')
    while True:
        matriceFin, listAlarm = smartFunction(listConso, listDispo)
        #print(f'getDispatcj = {listConso}')
        # await asyncio.sleep(0.15)
        await asyncio.sleep(2.15)

# variables certificat chiffrement
cert_idx = 1
# cert = f"peer-certificate-client-scada-{cert_idx}.der"
# private_key = f"peer-private-key-client-scada-{cert_idx}.pem"
cert = f"/certificates-all/certificate-scada-1.der"
private_key = f"private-key-scada-1.pem"

async def sendConsommationToGenerator(url):
    global consommationTotale
    global listCoeff, listCapa

    index = int(url.split('opc.tcp://server-gene')[1][:1]) - 1
    #print(f'index = {index}')
    client = Client(url=url)
    await client.set_security(
        SecurityPolicyBasic256Sha256,
        certificate=cert,
        private_key=private_key,
        server_certificate="/certificates-all/certificate-gene-1.der"
    )
    async with client :
        #print("TEst generateur connection")   
        uri = 'http://examples.freeopcua.github.io'
        idx = await client.get_namespace_index(uri)
        #conso = await client.nodes.root.get_child(["0:Objects", f"{idx}:Consommation", f"{idx}:consommation"])
       
        alarmeHandler = AlarmeHandler(url)
        # We create a Client Subscription.
        alarmeSubscription = await client.create_subscription(500, alarmeHandler)
        node = await client.nodes.root.get_child(["0:Objects", f"{idx}:Alarm", f"{idx}:alarme"])

        capacity = await client.nodes.root.get_child(["0:Objects", f"{idx}:Capa&Coeff", f"{idx}:capa"])
        #listCapa[index] = await capacity.read_value()
        listDispo[index] = await capacity.read_value()
        #listCapa.append(await capacity.read_value())
        #listDispo.append(await capacity.read_value())

        coeff = await client.nodes.root.get_child(["0:Objects", f"{idx}:Capa&Coeff", f"{idx}:coeff"])
        #listCoeff.append(await coeff.read_value())
        # We subscribe to data changes for 1 node, l'alarme du générateur.
        await alarmeSubscription.subscribe_data_change(node)
        conso = await client.nodes.root.get_child(["0:Objects", f"{idx}:Consommation", f"{idx}:consommation"])
        
        while True:
            consoTotale = 0
            # await asyncio.sleep(1)
            # await asyncio.sleep(2)
            await asyncio.sleep(4)
            
            for i in range(len(listConso)):
                print(f'matriceFin = {matriceFin[i][int(index)]}')
                consoTotale += matriceFin[i][int(index)]
            print(f"Sending {consoTotale} W of consommation to {url}")
            await conso.write_value(consoTotale)
        
        #return client
        

class AlarmeHandler:
    url_gene = ''
    def __init__(self, url):
        self.url_gene = url
    async def datachange_notification(self, node: Node, val, data):
        print(f'alarme = {val} depuis le gene {self.url_gene}')   



async def retrieveConsommationFromConsummer(url):
    global listConso
    client = Client(url=url)

    index = int(url.split('opc.tcp://server-conso')[1][:1]) - 1

    await client.set_security(
        SecurityPolicyBasic256Sha256,
        certificate=cert,
        private_key=private_key,
        server_certificate="/certificates-all/certificate-conso-1.der"
    )
    async with client:
        #print("TEst consommateur connection")              
        uri = 'http://examples.freeopcua.github.io'
        idx = await client.get_namespace_index(uri)
        consommationConsommateurObject = await client.nodes.root.get_child(["0:Objects", f"{idx}:Conso", f"{idx}:consommation"])
        #print(client.__str__())
        while True:
            # await asyncio.sleep(1.05)
            # await asyncio.sleep(2.05)
            await asyncio.sleep(4.05)
            listConso[index] = await consommationConsommateurObject.read_value()
            print(f'consommation = {listConso[int(index)]}')
    



async def main():
    NbConso = int(sys.argv[1])
    NbGene = int(sys.argv[2])
    print("NbConso : ",NbConso)
    print("NbGene : ",NbGene)
    taskList = []
    global listDispo, listConso, matriceFin
    listDispo = [0 for i in range(NbGene)]
    listConso = [0 for i in range(NbConso)]
    matriceFin = [[0 for i in range(len(listDispo))]for j in range(len(listConso))]

    # Creation des Generateurs et consommateurs
    for i in range(NbConso):
        url_conso = 'opc.tcp://server-conso'+str(i+1)+':4840/freeopcua/server/consommateur'
        print(url_conso)            
        taskList.append(retrieveConsommationFromConsummer(url_conso))
    taskList.append(getDispatch(listDispo, listConso))
    for i in range(NbGene):
        url_gene = 'opc.tcp://server-gene'+str(i+1)+':4840/freeopcua/server/'
        print(url_gene)
        taskList.append(sendConsommationToGenerator(url_gene))
    
    L = await asyncio.gather(*taskList)


import os 

if __name__ == '__main__':

#     cmd = ("openssl req -x509 -sha256 -nodes -days 365 -newkey rsa:2048 -config configuration_certs.cnf \
# -keyout /private-key-scada-1.pem -outform der -out /certificates-all/certificate-scada-1.der")
    # os.system(cmd)

    # os.system("sleep 3")

    if not os.path.isfile("/certificates-all/certificate-scada-1.der"):
        cmd = ("openssl req -x509 -sha256 -nodes -days 365 -newkey rsa:2048 -config configuration_certs.cnf \
-keyout /private-key-scada-1.pem -outform der -out /certificates-all/certificate-scada-1.der")
        os.system(cmd)
    else:
        print("FILE EXISTS")


    asyncio.run(main())



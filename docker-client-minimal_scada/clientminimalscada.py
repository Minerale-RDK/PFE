import asyncio
import sys

import logging
from asyncua import Client, Node, ua
from threading import Thread
from asyncua.crypto.security_policies import SecurityPolicyBasic256Sha256
from flask import Flask, render_template
import os

from multiprocessing import Process

clientminimalscada = Flask(__name__)

@clientminimalscada.route('/')
def home():
    global listConso,listDispo,matriceFin

    global matriceFin, alarmesGene, ecartDemCons
    
    matrice = matriceFin.copy()
    print(f'Matrice == {matrice}')
    generateur = len(matrice[0])
    conso = listConso.copy()
    prod = listDispo.copy()
    client= len(matrice)
    sum_client = ecartDemCons.copy()#Liste alarmes des consomateurs
    sum_gene = alarmesGene.copy()#Liste alarmes des genes
    print(f'Alarmes de sum_gene = {sum_gene}, alramres de sum_client {sum_client}')

    return render_template("index.html", client=client, generateur=generateur, mat = matrice, conso=conso, prod=prod, 
                                    sum_client =sum_client, sum_gene=sum_gene); 


consommationTotale = 0

listCoeff = []
listConso = []
listDispo = []
matriceFin = [[]]
listAlarm = []
ecartDemCons = []
alarmesGene = []

def orderGene(listConso, listDispo, listeCoeff, matricePrec, vitesseRemp):
    augmentation = True
    listeTrie = []
    matricePasTrie = [[0 for i in range(len(listDispo))]for j in range(len(listConso))]
    matriceTrie = [[0 for i in range(len(listDispo))]for j in range(len(listConso))]
    matricePrecTrie = [[0 for i in range(len(listDispo))]for j in range(len(listConso))]
    matricePrecCopy = matricePrec.copy()
    listDispoCopy = listDispo.copy()
    listConsoCopy = listConso.copy()
    indexListCroissant = sorted(range(len(listeCoeff)), key=lambda k: listeCoeff[k],reverse=True)
    for i in indexListCroissant:
        listeTrie.append(listDispo[i])
    for i in range(len(listConso)):
        for j in range(len(listDispo)):
            matricePrecTrie[i][j] = matricePrec[i][indexListCroissant[j]]
    matricePasTrie = smartFunction(listConso, listeTrie, listeCoeff, matricePrecTrie, 1)
    
    for i in range(len(listConso)):
        for j in range(len(listDispo)):
            matriceTrie[i][indexListCroissant[j]] = matricePasTrie[i][j]
    return matriceTrie
            
    
def smartFunction(listConso, listDispo, listeCoeff, matricePrec, vitesseRemp):
    matrice = [[0 for i in range(len(listDispo))]for j in range(len(listConso))]
    listConsoInit = listConso.copy()
    listeConsoCopy = listConso.copy()
    listeDispoCopy = listDispo.copy()
    listeCapa = listDispo.copy()
    listAlarm = []
    listEcartAP = []
    listeEcartNow = []
    listeSumEcart= []
    listePb = [0 for i in range(len(listDispo))]
    
    
    for y in range(vitesseRemp):        
        for j in range(len(listDispo)):
            while round(listeDispoCopy[j]*1/vitesseRemp) > 0:
                for i in range(len(listConso)):
                    demande = listeConsoCopy[i]
                    if demande <= round(listeDispoCopy[j]*1/vitesseRemp): #True - False
                        listeDispoCopy[j] -= demande #Dispo = 300
                        matrice[i][j] += demande#Case gene1 conso1 = 200
                        listeConsoCopy[i] = 0
                    else:
                        ecart = listeConsoCopy[i] - round(listeDispoCopy[j]*1/vitesseRemp) #Demande 400 Dispo 300 ecart = 100
                        listeDispoCopy[j] -= demande - ecart #Dispo = 0
                        matrice[i][j] += demande - ecart#Case gene1 conso1 = 200
                        listeConsoCopy[i] = ecart
                break
                
    for h in range(len(listeDispoCopy)):
        a=0
        for g in range(len(matrice)):
            a += matricePrec[g][h]
        listEcartAP.append(a)

    for h in range(len(listeDispoCopy)):
        a=0        
        for g in range(len(matrice)):           
            a += matrice[g][h]
        listeEcartNow.append(a)
    
    for h in range(len(listeEcartNow)):
        listeSumEcart.append(abs(listeEcartNow[h]-listEcartAP[h]))
    
    for h in range(len(listeDispoCopy)):
        if listeSumEcart[h] >= (listeCapa[h]*listeCoeff[h]):
            listePb[h] = 1
    if sum(listePb) == 0:
        return matrice
    
    else:
        if vitesseRemp != 10:
            return smartFunction(listConso, listDispo, listeCoeff, matricePrec, vitesseRemp+1)
        else:
            return matrice


async def getDispatch(listConso, listDispo, listeCoeff):
    global matriceFin, ecartDemCons
    matriceFin = [[0 for i in range(len(listDispo))]for j in range(len(listConso))]
    
    while True:
        listConsoCopy = listConso.copy()
        matriceFin = smartFunction(listConso, listDispo, listeCoeff,matriceFin,1 )
        ecartDemCons = [False for i in range(len(listConso))]
        for i in range(len(listConso)):
            if ((sum(matriceFin[i])+1)/(listConsoCopy[i]+1)) < 0.9:
                ecartDemCons[i] = True   
        print(f'ecartDemCons = {ecartDemCons}')
        print(f'matrice Fin = {matriceFin}')
        await asyncio.sleep(1)


# variables certificat chiffrement
'''
cert_idx = 1
cert = f"/certificates-all/certificate-scada-1.der"
private_key = f"private-key-scada-1.pem"
'''

async def sendConsommationToGenerator(url):
    global consommationTotale
    global listCoeff, listCapa

    index = int(url.split('opc.tcp://server-gene')[1][:1]) - 1
    client = Client(url=url)
    '''
    await client.set_security(
        SecurityPolicyBasic256Sha256,
        certificate=cert,
        private_key=private_key,
        server_certificate=f"/certificates-all/certificate-gene-{index+1}.der"
    )
    '''
    
    async with client :
        #print(f"TEst generateur connection et url = {url}")   
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
        
        listCoeff[int(index)] = await capacity.read_value()*await coeff.read_value()
        print(f'liste coeff = {listCoeff}, index = {index}, listeConso = {listConso}')
       
        # We subscribe to data changes for 1 node, l'alarme du générateur.
        await alarmeSubscription.subscribe_data_change(node)
        conso = await client.nodes.root.get_child(["0:Objects", f"{idx}:Consommation", f"{idx}:consommation"])
        
        while True:
            consoTotale = 0
            await asyncio.sleep(1.5)
            # await asyncio.sleep(2)
            # await asyncio.sleep(4)
            
            for i in range(len(listConso)):
                consoTotale += matriceFin[i][int(index)]
                print(f"Sending {consoTotale} W of consommation to {url}")
                await conso.write_value(consoTotale)
        
        #return client
        

class AlarmeHandler:
    url_gene = ''
    global alarmesGene
    def __init__(self, url):       
        self.url_gene = url
    async def datachange_notification(self, node: Node, val, data):
        alarmesGene[int(self.url_gene.split('opc.tcp://server-gene')[1][:1]) - 1] = val  



async def retrieveConsommationFromConsummer(url):
    global listConso
    client = Client(url=url)

    index = int(url.split('opc.tcp://server-conso')[1][:1]) - 1

    '''
    await client.set_security(
        SecurityPolicyBasic256Sha256,
        certificate=cert,
        private_key=private_key,
        server_certificate=f"/certificates-all/certificate-conso-{index+1}.der"
    )
    '''

    async with client:
        #print("TEst consommateur connection")              
        uri = 'http://examples.freeopcua.github.io'
        idx = await client.get_namespace_index(uri)
        consommationConsommateurObject = await client.nodes.root.get_child(["0:Objects", f"{idx}:Conso", f"{idx}:consommation"])
        #print(client.__str__())
        while True:
            await asyncio.sleep(1.5)
            # await asyncio.sleep(4.05)
            listConso[index] = await consommationConsommateurObject.read_value()
            print(f'consommation = {listConso[index]} à l\'index {index}')
    

async def main():
    NbConso = int(sys.argv[1])
    NbGene = int(sys.argv[2])
    # print("NbConso : ",NbConso)
    # print("NbGene : ",NbGene)
    taskList = []
    global listDispo, listConso, listCoeff, matriceFin, ecartDemCons, alarmesGene
    listDispo = [0 for i in range(NbGene)]
    listConso = [0 for i in range(NbConso)]
    listCoeff = [0 for i in range(NbGene)]
    ecartDemCons = [0 for i in range(NbConso)]
    alarmesGene = [0 for i in range(NbGene)]
    matriceFin = [[0 for i in range(len(listDispo))]for j in range(len(listConso))]

    # Creation des Generateurs et consommateurs
    for i in range(NbConso):
        url_conso = 'opc.tcp://server-conso'+str(i+1)+':4840/freeopcua/server/consommateur'         
        taskList.append(retrieveConsommationFromConsummer(url_conso))
    taskList.append(getDispatch(listConso, listDispo,listCoeff))
    for i in range(NbGene):
        url_gene = 'opc.tcp://server-gene'+str(i+1)+':4840/freeopcua/server/'
        taskList.append(sendConsommationToGenerator(url_gene))
    
    L = await asyncio.gather(*taskList)


import os

def starter():
    print("LAUCHING")
    asyncio.run(main())


if __name__ == '__main__':

    os.system("sleep 3")
    port = int(os.environ.get('PORT', 5000))

    p = Thread(target=starter)
    p.start()


    clientminimalscada.run(debug=True, host='0.0.0.0', port=port,use_reloader=True)



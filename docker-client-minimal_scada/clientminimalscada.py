import asyncio
import sys,os

import logging
from asyncua import Client, Node, ua
from threading import Thread
from asyncua.crypto.security_policies import SecurityPolicyBasic256Sha256
from flask import Flask, render_template, request

clientminimalscada = Flask(__name__)

@clientminimalscada.route('/',methods=["GET"])
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

    liste = { "matrice" : matrice, "sum_gene" : sum_gene, "sum_client":sum_client, "listeal":sum_gene, 'conso': conso}
    text = request.args.get('jsdata')
    if text:
        return liste

    return render_template("index.html", client=client, generateur=generateur, mat = matrice, conso=conso, prod=prod, 
                                    sum_client =sum_client, sum_gene=sum_gene)



consommationTotale = 0

listCoeff = []
listConso = []
listDispo = []
matriceFin = [[]]
matriceFinMoins1 = [[]]
listAlarm = []
ecartDemCons = []
alarmesGene = []
ecartScadaGene = []

def orderGene(listConso, listDispo, listeCoeff, matricePrec, vitesseRemp):
    listeTrie = []
    listDispoReel = [0 for i in range(len(listDispo))]
    listConsoPrec = [0 for i in range(len(listDispo))]
    matricePasTrie = [[0 for i in range(len(listDispo))]for j in range(len(listConso))]
    matriceTrie = [[0 for i in range(len(listDispo))]for j in range(len(listConso))]
    matricePrecTrie = [[0 for i in range(len(listDispo))]for j in range(len(listConso))]
    matricePrecCopy = matricePrec.copy()
    listDispoCopy = listDispo.copy()
    listConsoCopy = listConso.copy()
    indexListCroissant = sorted(range(len(listeCoeff)), key=lambda k: listeCoeff[k],reverse=True)

    
    for i in range(len(matricePrec[0])):
        for j in range(len(matricePrec)):
            listConsoPrec[i] += matricePrec[j][i] 
            
    for i in range(len(listConsoPrec)):
        if listConsoPrec[i] + listeCoeff[i] >= listDispo[i]:
            listDispoReel[i] = listDispo[i]
        else:
            listDispoReel[i] = listConsoPrec[i] + listeCoeff[i]
    print(f'list dispo réel = {listDispoReel}, liste dispo = {listDispo}, listeConsoPrec = {listConsoPrec}')

    for i in indexListCroissant:
        listeTrie.append(listDispoReel[i])
    for i in range(len(listConso)):
        for j in range(len(listDispo)):
            matricePrecTrie[i][j] = matricePrec[i][indexListCroissant[j]]
    matricePasTrie = smartFunction(listConso, listeTrie, listeCoeff, matricePrecTrie, 2, listDispoCopy)
    
    for i in range(len(listConso)):
        for j in range(len(listDispo)):
            matriceTrie[i][indexListCroissant[j]] = matricePasTrie[i][j]
    return matriceTrie
            
    
def smartFunction(listConso, listDispo, listeCoeff, matricePrec, vitesseRemp, listCapa):
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
    print(f'at the lDispo = {listeDispoCopy}, lCon = {listeConsoCopy} vit remp = {vitesseRemp}')
    
    for i in range(vitesseRemp):
        for y in range(len(listeConsoCopy)):
            while round(listeConsoCopy[y]/vitesseRemp) != 0:
                for h in range(len(listeDispoCopy)):
                    if round(listeConsoCopy[y]/2) < listeDispoCopy[h]:
                        matrice[y][h] += int(round(listeConsoCopy[y]/vitesseRemp))
                        listeDispoCopy[h] -= int(round(listeConsoCopy[y]/vitesseRemp))
                        listeConsoCopy[y] -= int(round(listeConsoCopy[y]/vitesseRemp))
                        continue
                    else:
                        matrice[y][h] += listeDispoCopy[h]
                        listeConsoCopy[y] -= listeDispoCopy[h]
                        listeDispoCopy[h] = 0
                if sum(listeDispoCopy) == 0:
                    break
    for y in range(len(listeConsoCopy)):
            while round(listeConsoCopy[y]) != 0:
                for h in range(len(listeDispoCopy)):
                    if round(listeConsoCopy[y]/2) < listeDispoCopy[h]:
                        matrice[y][h] += int(round(listeConsoCopy[y]))
                        listeDispoCopy[h] -= int(round(listeConsoCopy[y]))
                        listeConsoCopy[y] -= int(round(listeConsoCopy[y]))
                        continue
                    else:
                        matrice[y][h] += listeDispoCopy[h]
                        listeConsoCopy[y] -= listeDispoCopy[h]
                        listeDispoCopy[h] = 0
                if sum(listeDispoCopy) == 0:
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
        if listeSumEcart[h] >= listeCapa[h]/2:
            listePb[h] = 1
    if sum(listePb) == 0:
        return matrice
    
    else:
        if vitesseRemp != 10:
            return smartFunction(listConso, listDispo, listeCoeff, matricePrec, vitesseRemp+1, listCapa)
        else:
            return matrice


async def getDispatch(listConso, listDispo, listeCoeff):
    global matriceFin, ecartDemCons, matriceFinMoins1
    matriceFin = [[0 for i in range(len(listDispo))]for j in range(len(listConso))]

    
    while True:
        listConsoCopy = listConso.copy()
        matriceFinMoins1 = matriceFin.copy()
        matriceFin = orderGene(listConso, listDispo, listeCoeff,matriceFin,1 )
        ecartDemCons = [False for i in range(len(listConso))]
        for i in range(len(listConso)):
            if ((sum(matriceFin[i])+1)/(listConsoCopy[i]+1)) < 0.9:
                ecartDemCons[i] = True   
        print(f'ecartDemCons = {ecartDemCons}')
        print(f'matrice Fin = {matriceFin}')
        await asyncio.sleep(1)


# variables certificat chiffrement
cert_idx = 1
cert = f"/certificates-all/certificate-scada-1.der"
private_key = f"private-key-scada-1.pem"

async def sendConsommationToGenerator(url):
    global consommationTotale
    global listCoeff, listCapa, ecartScadaGene

    index = int(url.split('opc.tcp://server-gene')[1][:1]) - 1
    client = Client(url=url)
    
    await client.set_security(
        SecurityPolicyBasic256Sha256,
        certificate=cert,
        private_key=private_key,
        server_certificate=f"/certificates-all/certificate-gene-{index+1}.der"
    )
    
    async with client :
        uri = 'http://examples.freeopcua.github.io'
        idx = await client.get_namespace_index(uri)
       
        prodAct = await client.nodes.root.get_child(["0:Objects", f"{idx}:Freq&Prod", f"{idx}:production"])
        node = await client.nodes.root.get_child(["0:Objects", f"{idx}:Alarm", f"{idx}:alarme"])

        capacity = await client.nodes.root.get_child(["0:Objects", f"{idx}:Capa&Coeff", f"{idx}:capa"])
        listDispo[index] = await capacity.read_value()

        coeff = await client.nodes.root.get_child(["0:Objects", f"{idx}:Capa&Coeff", f"{idx}:coeff"])
        
        listCoeff[int(index)] = await capacity.read_value()*await coeff.read_value()
        print(f'liste coeff = {listCoeff}, index = {index}, listeConso = {listConso}')
       
        conso = await client.nodes.root.get_child(["0:Objects", f"{idx}:Consommation", f"{idx}:consommation"])

        
        initStart = 0
        while True:
            consoTotale = 0
            consoTotaleMoins1 = 0
            initStart += 1
            await asyncio.sleep(1)        
            for i in range(len(listConso)):
                consoTotale += matriceFin[i][int(index)]
                consoTotaleMoins1 += matriceFinMoins1[i][int(index)]
            print(f'consototale moins 1 = {consoTotaleMoins1} et prod Act = { await prodAct.read_value()}')
            prodActNow = await prodAct.read_value()
            if initStart > 15:
                if prodActNow/consoTotaleMoins1 < 0.3 and prodActNow/consoTotale < 0.3 :
                    ecartScadaGene[int(index)] += 1
                else:
                    ecartScadaGene[int(index)] = 0
            if ecartScadaGene[int(index)] > 4:
                print(f'ALERTE GENERALLEEEEEEEEEE et index = {index}')
                listDispo[int(index)] = 0
                alarmesGene[int(index)] = 2
                break                
            else:
                alarmesGene[int(index)] = await node.read_value()  
            print(f"Sending {consoTotale} W of consommation to {url}")
            await conso.write_value(int(consoTotale))
        

async def retrieveConsommationFromConsummer(url):
    global listConso
    client = Client(url=url)

    index = int(url.split('opc.tcp://server-conso')[1][:1]) - 1
    
    await client.set_security(
        SecurityPolicyBasic256Sha256,
        certificate=cert,
        private_key=private_key,
        server_certificate=f"/certificates-all/certificate-conso-{index+1}.der"
    )
    
    async with client:           
        uri = 'http://examples.freeopcua.github.io'
        idx = await client.get_namespace_index(uri)
        consommationConsommateurObject = await client.nodes.root.get_child(["0:Objects", f"{idx}:Conso", f"{idx}:consommation"])
        while True:
            await asyncio.sleep(2)
            listConso[index] = await consommationConsommateurObject.read_value()
            print(f'consommation = {listConso[index]} à l\'index {index}')
    

async def main():
    NbConso = int(sys.argv[1])
    NbGene = int(sys.argv[2])
    # print("NbConso : ",NbConso)
    # print("NbGene : ",NbGene)
    taskList = []
    global listDispo, listConso, listCoeff, matriceFin, matriceFinMoins1, ecartDemCons, alarmesGene,ecartScadaGene
    listDispo = [0 for i in range(NbGene)]
    listConso = [0 for i in range(NbConso)]
    listCoeff = [0 for i in range(NbGene)]
    ecartDemCons = [0 for i in range(NbConso)]
    alarmesGene = [0 for i in range(NbGene)]
    ecartScadaGene = [0 for i in range(NbGene)]
    matriceFin = [[0 for i in range(len(listDispo))]for j in range(len(listConso))]
    matriceFinMoins1 = [[0 for i in range(len(listDispo))]for j in range(len(listConso))]

    # Creation des Generateurs et consommateurs
    for i in range(NbConso):
        url_conso = 'opc.tcp://server-conso'+str(i+1)+':4840/freeopcua/server/consommateur'         
        taskList.append(retrieveConsommationFromConsummer(url_conso))
    taskList.append(getDispatch(listConso, listDispo,listCoeff))
    for i in range(NbGene):
        url_gene = 'opc.tcp://server-gene'+str(i+1)+':4840/freeopcua/server/'
        taskList.append(sendConsommationToGenerator(url_gene))
    
    L = await asyncio.gather(*taskList)


def starter():
    print("LAUCHING")
    asyncio.run(main())


if __name__ == '__main__':

    os.system("sleep 3")
    port = int(os.environ.get('PORT', 5000))

    p = Thread(target=starter)
    p.start()


    clientminimalscada.run(debug=True, host='0.0.0.0', port=port)



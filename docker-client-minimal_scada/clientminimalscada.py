import asyncio
import sys,os

import logging
from asyncua import Client, Node, ua
from threading import Thread
from asyncua.crypto.security_policies import SecurityPolicyBasic256Sha256
from flask import Flask, render_template, request

clientminimalscada = Flask(__name__)

#Flask pour l'interface web
@clientminimalscada.route('/',methods=["GET"])
def home():
    global listConso,listDispo,matriceFin

    global matriceFin, alarmesGene, ecartDemCons
    
    matrice = matriceFin.copy()
    print(f'Matrice == {matrice}')
    generateur = len(matrice[0])#Nombre de générateurs
    conso = listConso.copy()#Liste de consommation
    prod = listDispo.copy()#Liste de capacités
    client= len(matrice)#Nombre de clients
    sum_client = ecartDemCons.copy()#Liste alarmes des consomateurs
    sum_gene = alarmesGene.copy()#Liste alarmes des genes

    liste = { "matrice" : matrice, "sum_gene" : sum_gene, "sum_client":sum_client, "listeal":sum_gene, 'conso': conso}
    text = request.args.get('jsdata')
    if text:
        return liste

    return render_template("index.html", client=client, generateur=generateur, mat = matrice, conso=conso, prod=prod, 
                                    sum_client =sum_client, sum_gene=sum_gene)



# Initialisation des variables globales du SCADA
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

#Cette fonction trie les générateurs par ordre décroissant de coefficient de vitesse. Les générateurs pouvant
#s'allumer et s'éteindre le plus vite sont placés en premiers. Cela est du au fait que s'il y a une chute de
#consommation, ce sont ceux qui absorberont le plus vite cet écart
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

    #Cette partie de la fonction sert à calculer la disponibilité réelle : on calcule ici 
    #la somme des consos de chaque génération à t-1
    for i in range(len(matricePrec[0])):
        for j in range(len(matricePrec)):
            listConsoPrec[i] += matricePrec[j][i] 
    
    #A la place de leur capacité réelle, on donne comme dispo réelle à la smart function le
    #maximum que chaque générateur peut produire sans avoir de chute de fréquence.
    for i in range(len(listConsoPrec)):
        if listConsoPrec[i] + listeCoeff[i] >= listDispo[i]:
            listDispoReel[i] = listDispo[i]
        else:
            listDispoReel[i] = listConsoPrec[i] + listeCoeff[i]

    for i in indexListCroissant:
        listeTrie.append(listDispoReel[i])
    for i in range(len(listConso)):
        for j in range(len(listDispo)):
            matricePrecTrie[i][j] = matricePrec[i][indexListCroissant[j]]

    #On appelle ici la smartFunction qui fais la distribution de l'électricité "intelligement"
    matricePasTrie = smartFunction(listConso, listeTrie, listeCoeff, matricePrecTrie, 2, listDispoCopy) 
    
    #On retrie la matrice dans le bon ordre pour l'affichage
    for i in range(len(listConso)):
        for j in range(len(listDispo)):
            matriceTrie[i][indexListCroissant[j]] = matricePasTrie[i][j]
    return matriceTrie
            

#Cette fonction s'occupe de la distribution 'intelligente' de l'électricité entre les générateurs.
#La vitesse de remplissage (vitesseRemp) permet de vider chaque générateur petit à petit au lieu de
#vider complétement le premier, puis le deuxième ... pour plus de réalisme et répartir la charge. Cette
#valeur est fixée à deux au départ pour les vider par moitié.
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
    
    #On fait la répartition entre les générateurs jusqu'à ce que l'une des deux listes soit vide
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

    #Ici, on calcule les écarts entre la production précédente et celle demandée  
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
    #Si cela ne va pas générer d'alarme, on s'arrête là
    if sum(listePb) == 0:
        return matrice
    
    #Sinon, on recommence en augmentant vitesseRemp pour mieux répartir entre les générateurs en les remplissants par
    #tiers, quarts etc. jusqu'à dix où on s'arrête dans tous les cas 
    else:
        if vitesseRemp != 10:
            return smartFunction(listConso, listDispo, listeCoeff, matricePrec, vitesseRemp+1, listCapa)
        else:
            return matrice


#C'est la fonction appelée pour générer la distribution
async def getDispatch(listConso, listDispo, listeCoeff):
    global matriceFin, ecartDemCons, matriceFinMoins1
    matriceFin = [[0 for i in range(len(listDispo))]for j in range(len(listConso))]
   
    while True:
        listConsoCopy = listConso.copy()
        matriceFinMoins1 = matriceFin.copy()
        matriceFin = orderGene(listConso, listDispo, listeCoeff,matriceFin,1 )
        #On vérifie si il n'y a pas d'écart entre ce qui est demandée par les clients et fourni par les générateurs
        #Si un client ne recoit pas au moins 90% de sa demande, une alarme est générée au niveau du client
        ecartDemCons = [False for i in range(len(listConso))]
        for i in range(len(listConso)):
            if ((sum(matriceFin[i])+1)/(listConsoCopy[i]+1)) < 0.9:
                ecartDemCons[i] = True   
        await asyncio.sleep(1)


# variables certificat chiffrement
cert_idx = 1
cert = f"/certificates-all/certificate-scada-1.der"
private_key = f"private-key-scada-1.pem"

#Cette fontion est appelée pour chaque générateur pour leur fournir la production demandée par le SCADA
async def sendConsommationToGenerator(url):
    global consommationTotale
    global listCoeff, listCapa, ecartScadaGene

    index = int(url.split('opc.tcp://server-gene')[1][:1]) - 1
    client = Client(url=url)
    #Certificats
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
            prodActNow = await prodAct.read_value()
            #On vérifie ici si ce qui est demandé par le SCADA et effectivement produit par le générateur
            #correspond pour identifier si le générateur est HACKED. On attend 15 itération car l'initialisation
            #peut provoquer des disfonctionnements
            if initStart > 15:
                if prodActNow/consoTotaleMoins1 < 0.3 and prodActNow/consoTotale < 0.3 :
                    ecartScadaGene[int(index)] += 1
                else:
                    ecartScadaGene[int(index)] = 0
            #Si il y a un écart significatif entre la demande du SCADA et la prod du générateur 4 fois d'affilée
            #on passe le générateur en HACKED et passe sa dispo à 0 pour l'isoler du réseau
            if ecartScadaGene[int(index)] > 4:
                listDispo[int(index)] = 0
                alarmesGene[int(index)] = 2
                break                
            else:
                alarmesGene[int(index)] = await node.read_value()  
            print(f"Sending {consoTotale} W of consommation to {url}")
            await conso.write_value(int(consoTotale))
        
#Fonction pour récuppérer la consommation par consommateur
async def retrieveConsommationFromConsummer(url):
    global listConso
    client = Client(url=url)

    index = int(url.split('opc.tcp://server-conso')[1][:1]) - 1
    #Certificats
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
    

async def main():
    #Initialisations
    NbConso = int(sys.argv[1])
    NbGene = int(sys.argv[2])
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



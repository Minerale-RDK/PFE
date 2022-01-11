#!/bin/bash

#initialise le compteur
count=1
echo "1/ count is : $count"

#créer un réseau pour connecter les conteneurs 
docker network create -d bridge network_0.1
docker network create -d bridge network_0.2


#construit les images
docker image build -t serveur-consommateur docker-server-minimal_consommateur/
docker image build -t serveur-generateur docker-server-minimal_generateur/v0.1.0/
docker image build -t client_scada docker-client-minimal_scada/v0.0.1/
docker image build -t client_captor docker-client-minimal_captor/v0.0.1/


#lance le serveur-gene1, serveur-generateur
docker run --rm -d --env GENE=500 --name server-gene$count --network=network_0.1 serveur-generateur

##lance le serveur-conso1, serveur-consommateur
docker run --rm -d --env CONSO=300 --name server-conso$count --network=network_0.1 serveur-consommateur


count=$(($count+1))

docker run --rm -d --env GENE=600 --name server-gene$count --network=network_0.2 serveur-generateur
docker run --rm -d --env CONSO=470 --name server-conso$count --network=network_0.2 serveur-consommateur

#Il est nécessaire de faire cet opération pour laisser les premières connexions s'établir
##echo "sleep"
sleep 6
##echo "wake up"

#lance le client Scada
docker run -d --rm --name client1-scada --env COUNT=1 --network=network_0.1 client_scada 
docker run -d --rm --name client1-captor --env COUNT=1 --network=network_0.1 client_captor 
#docker run --rm --name client2 --env COUNT=$count --network=network_0.2 client 


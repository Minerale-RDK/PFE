#!/bin/bash

#initialise le compteur
count=1
echo "1/ count is : $count"

#créer un réseau pour connecter les conteneurs 
docker network create -d bridge network_0.1


#construit les images
docker image build -t serveur-consommateur docker-server-minimal_consommateur/
docker image build -t serveur-generateur docker-server-minimal_generateur/v0.1.0/
docker image build -t client docker-client-minimal_scada/v0.0.1/


#lance le serveur-gene1, serveur-generateur
docker run -d --env GENE=500 --name server-gene$count --network=network_0.1 serveur-generateur

##lance le serveur-conso1, serveur-consommateur
docker run -d --env CONSO=300 --name server-conso$count --network=network_0.1 serveur-consommateur

#Il est nécessaire de faire cet opération pour laisser les premières connexions s'établir
##echo "sleep"
sleep 6
##echo "wake up"

#lance le client Scada
docker run --name client1 --env COUNT=1 --network=network_0.1 client 

#!/bin/bash

#initialise le compteur
count=1
echo "1/ count is : $count"

#créer un réseau pour connecter les conteneurs 
docker network create -d bridge


#construit les images
docker image build -t serveur-consommateur docker-server-minimal_consommateur/
docker image build -t serveur-generateur docker-server-minimal_generateur/
docker image build -t client docker-client-minimal_scada/


#lance le serveur-gene1, serveur-generateur
docker run -d --env GENE=500 --name server-gene0 serveur-generateur

##lance le serveur-conso1, serveur-consommateur
docker run -d --env CONSO=300 --name server-conso0 serveur-consommateur

#Il est nécessaire de faire cet opération pour laisser les premières connexions s'établir
sleep 6

#lance le client Scada
docker run --name client1 --env COUNT=1 client 

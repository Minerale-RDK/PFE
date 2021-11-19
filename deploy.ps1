#initialise le compteur
count=1

#créer un réseau pour connecter les conteneurs 
docker network create -d bridge network_0.1

#construit les images
docker image build -t serveur-consommateur docker-server-minimal_consommateur/
docker image build -t serveur-generateur docker-server-minimal_generateur/v0.1.0/
docker image build -t client docker-client-minimal_scada/v0.0.1/


#lance le serveur1, serveur-generateur
docker run --rm -d --name server$count --network=network_0.1 serveur-generateur&&

count++

##lance le serveur2, serveur-consommateur
docker run --rm -d --name server$count --network=network_0.1 serveur-consommateur&&

#Il est nécessaire de faire cet opération pour laisser les premières connexions s'établir
##echo "sleep"
sleep 6
##echo "wake up"

#lance le client scada
docker run --rm --name client --network=network_0.1 client 


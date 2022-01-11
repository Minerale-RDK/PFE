# Description

Repository du code pour le PFE sur la sécurité des Smart Grid

# Prérequis

Avec pip et python > 3.7

    pip install asyncua

# Usage

L'utilisation actuelle se fait avec Docker. Les commandes suivantes sont exécutées avec PowerShell, mais sont noramlement les mêmes (attention aux '\') pour bash.

```powershell

docker network create -d bridge network_0.1

cd C:\<Your Path>\Docker\docker-server-minimal_consommateur>
docker image build -t server-minimal_consommateur_0.1.0 .
docker run --name server1 --network network_0.1 serveur-minimal_consommateur_0.1.0

cd C:\<Your Path>\Docker\docker-server-minimal_generateur\<version x.x.x> >
docker image build -t server-minimal_generateur_0.1.0 .
docker run --name server2 --network network_0.1 serveur-minimal_generateur_0.1.0

cd C:\<Your Path>\Docker\docker-client-minimal_scada\<version x.x.x> >
docker image build -t client-minimal_scada_0.1.0 .
docker run --name client1 --network network_0.1 serveur-minimal_client_0.1.0


```

# Attention

L'ajout des valeurs de base fréquence et consommation se font en dur dans la ligne de commande du dockerfile. Pour modifier ces valeurs, le faire directement dans le dockerfile ou l'implémenter.

# A FAIRE (par ordre d'importance)

* Mettre en place chiffrement, signatures, mots de passe
* Simuler partie physique avec un réseau isolé et des capteurs
* Mécanisme de souscription pour ne pas requêter à chaque fois le serveur mais que le serveur envoie une notif si ça change
* Linker plusieurs scada pour simuler plusieurs quartiers
* Mettre boucle/redondance (production / scada)
* 
* Interface graphique
* 
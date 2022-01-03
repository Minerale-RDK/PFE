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

* Rajouter les fluctuations de consommation côté consommateur (voir google colab Drive)
* Faire un script permettant le déploiement en une commande de tous les containers
* Réfléchir à un moyen de pouvoir réaliser une mise à l'échelle (Comment récuppérer les adresses ip, les linker, faire plusieurs réseaux ?)
* Ajouter les panneaux solaires
* Linker plusieurs scada pour simuler plusieurs quartiers
* Mettre en place chiffrement, signatures, mots de passe
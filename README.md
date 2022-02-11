# SimuSec - PFE Ece Paris

## Description du projet

Ce projet est un outil de simulation de Smart-Grid permettant de tester la robustesse de celle-ci contre certaines cyber-attaques.

![Smart-Grid en fonctionnement](https://s10.gifyu.com/images/Hnet-image97594f3d00dbdce8.gif)

En l'état, le projet permet de :
+ Génerer X générateurs
	 + Choisir la capacité maximum de production de chaque générateur
	 + Choisir un coefficient de vitesse d'allumage et/ou extinction pour silmuler les différents types de générateurs (charbon, nucléaire ...)
+ Générer N Clients
	* Choisir leur consommation moyenne

+ Tester des cyber-attaques sur le réseau:
	* Mot de passe faible en ssh
	* Certificats falsifiés
	* Simulation d'intrusion physique (contournement pare-feu)
	* Attaque depuis un poste vers un autre

+ Mettre en place des remédiations aux attaques présentées précédement:
	* Mise en place de certificats (OPC-UA)
	* Mise en place de pare-feu sur le réseau (iptables)
	* Mise en place de pare-feu entre les équipemments (iptables)

## Présentation technique

Ce projet a été réalisé en utilisant le protocole OPC-UA via python grâce à la librairie [opcua-asyncio](https://github.com/FreeOpcUa/opcua-asyncio). Chaque client et générateur ainsi que le SCADA est sur son propre container Docker. Flask est utilisé pour créer l'interface web de visualisation. Par défaut, l'interface se trouve à l'adresse http://localhost:5000. Le projet est fonctionnel sur Linux uniquement. 

## Usage

Utiliser cette commande pour lancer l'interface graphique de génération de la Smart Grid :

```bash
sh start_all.sh
```

Pour arrêter la Smart Grid :

```bash
docker-compose down
```
Pour relancer la Smart Grid :

```bash
docker-compose up --build
```

Pour arrêter et supprimer la Smart-Grid :

```bash
sh erase.sh
```

Pour les attaques, se référer au fichier hack.txt ⚠️ Pour la première attaque (Hack Script 1), une version sans les certificats est nécessaire. Pour cela :
+ Arrêter la Smart Grid (docker-compose down)
+ Commenter les parties faisant appel aux certificats dans les fichier pyton du SCADA, du générateur et du consommateur
+ Relancer la Smart Grid (docker-compose up --build)
+ Lancer l'attaque grâce au fichier hack.txt

## Présenation des choix réalisés dans l'implémentation de la Smart Grid

#### Le calcul de la fréquence est réalisé comme ceci :

f1 = (production - consommation)/capacité + f0 

Avec f0 = 50. 

Un écart de + ou - 0.5 autour de 50 génère une alarme de chute ou d'augmentation de fréquence.

#### En cas d'alarme, une icône de l'Europe apparaît

Cela représente le 'partenaire européen' qui intervient pour combler le manque d'électricité pour les clients n'en recevant pas assez, ou pour acheter l'électricité produite en trop.

#### Distribution intelligente d'électricité (smartFunction)

Les générateurs possèdent un seuil d'écart de production entre deux itérations au-delà duquel une augmentation ou une chute de fréquence aura lieue. Ce seuil est égal à la moitié de la capacité du générateur, et provient directement de la formule ci-dessus. 

Exemple : Si G1 à une capacité maximale de produtcion = 500 :

Si il produit 50 à t-1 et que le SCADA lui réclame 150 à t :

Ecart = 150 - 50 = 100

Seuil = 500/2 = 250

100 < 250 : Pas d'alarme 

Si il produit 50 à t-1 et que le SCADA lui réclame 450 à t :

Ecart = 450 - 50 = 400

Seuil = 500/2 = 250

400 > 250 : Alarme

Comme le SCADA connait le seuil et la production à t-1 de chaque générateur, il ne demandera jamais à un générateur une nouvelle production dépassant son seuil. Par contre, si la consommation des clients chute drastiquement, il ne peut rien faire et il y aura une augementation de la fréquence.

Le SCADA "vide" d'abord les générateurs par moitié pour répartir la charge entre les générateurs. Si cette répartition va générer des alertes, il recommence en "vidant" les générateurs par tiers pour répartir la charge de façon encore plus équivalente. Il recommence par quart, cinquième etc. jusqu'à dixième où il s'arrête dans tous les cas. Cela est nécessaire pour un retour à la normale le plus rapide possible.

#### Améliorations possibles

* Rendre utilisable le SCADA rescue (de secours)
* Implémenter les clients (consommateurs) producteurs d'énergie
* Faire varier la capacité maximale de certains générateurs pour simuler des productions d'énergies renouvelables (conditions météos changeantes par exemple)
* Mise en place de plusieurs SCADA
* Déploiement dans le Cloud pour optimisation des performances

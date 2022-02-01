import logging
import asyncio
import sys
sys.path.insert(0, "..")

from asyncua import ua, Server
from asyncua.common.methods import uamethod

import random
import time
import math

from asyncua.crypto.permission_rules import SimpleRoleRuleset
from asyncua.server.users import UserRole
from asyncua.server.user_managers import CertificateUserManager

starttime=time.time()

@uamethod
def func(parent, value):
    return value * 2

def Consumption(cpt,consumption):
    # Nuit
    if (cpt in range (0,7)):
        consommation = random.uniform(0.75*consumption,1.04*consumption)
    # Matin
    elif (cpt in range (7,11)):
        consommation = random.uniform(1.10*consumption,1.32*consumption)
    # Après-midi
    elif (cpt in range (11,19)):
        consommation = random.uniform(0.75*consumption,1.04*consumption)
    # Soir
    elif (cpt in range (19,22)):
        consommation = random.uniform(2.02*consumption,2.34*consumption)
    elif (cpt in range (22,24)):
        consommation = random.uniform(0.01*consumption,0.1*consumption)
    return int(consommation)


async def main():
    _logger = logging.getLogger('asyncua')

    # server encryption  
    '''
    cert_user_manager = CertificateUserManager()
    await cert_user_manager.add_admin("certificates-all/certificate-scada-1.der", name='admin_scada')
    '''
    # setup our server
    consommation  = int(sys.argv[1])
    
    server = Server()#user_manager=cert_user_manager)
    
    await server.init()
    server.set_endpoint('opc.tcp://0.0.0.0:4840/freeopcua/server/consommateur')

    # Security policy  
    '''
    server.set_security_policy([ua.SecurityPolicyType.Basic256Sha256_SignAndEncrypt], permission_ruleset=SimpleRoleRuleset())
    '''

    # Load server certificate and private key.
    # This enables endpoints with signing and encryption.
    '''   
    await server.load_certificate("/certificates-all/certificate-conso-1.der")
    await server.load_private_key("private-key-conso-1.pem")
    '''

    ##DEBUG
    print("##DEBUG\n CONSO consomme {} W \n##### ".format(consommation))


    # setup our own namespace, not really necessary but should as spec
    uri = 'http://examples.freeopcua.github.io'
    idx = await server.register_namespace(uri)

    # populating our address space
    # server.nodes, contains links to very common nodes like objects and root
    objectConso = await server.nodes.objects.add_object(idx, 'Conso')
    consommation1 = await objectConso.add_variable(idx, 'consommation', 0)
    # Set MyVariable to be writable by clients
    await consommation1.set_writable()
    await server.nodes.objects.add_method(ua.NodeId('ServerMethod', 2), ua.QualifiedName('ServerMethod', 2), func, [ua.VariantType.Int64], [ua.VariantType.Int64])
    print('Starting server!')
    cpt = 0
    #j = 0
    async with server:
        while True:
            # await asyncio.sleep(1)
            #await asyncio.sleep(2)
            await asyncio.sleep(2)
            consommationHoraire = Consumption(cpt,consommation)
            print(f'consommationHoraire = {consommationHoraire}')
            #consommation+=1
            #print("consommation cote consommateur : {} à {}h ".format(consommationHoraire, cpt))
            await consommation1.write_value(consommationHoraire)
            #print(consommation)
            cpt+=1
            if (cpt == 24):
                #j += 1
                print ('Nouveau Jour')
                cpt = 0


import os 

if __name__ == '__main__':
    '''
    if not os.path.isfile("/certificates-all/certificate-conso-1.der"):
        cmd = ("openssl req -x509 -sha256 -nodes -days 365 -newkey rsa:2048 -config configuration_certs.cnf \
-keyout /private-key-conso-1.pem -outform der -out /certificates-all/certificate-conso-1.der")
        os.system(cmd)
    else:
        print("FILE EXISTS")
    '''

    
    asyncio.run(main(), debug=False)
import logging
import asyncio
import sys,os,json

from asyncua import ua, Server
from asyncua.common.methods import uamethod

import random
import math

from asyncua.crypto.permission_rules import SimpleRoleRuleset
from asyncua.server.users import UserRole
from asyncua.server.user_managers import CertificateUserManager

<<<<<<< HEAD
# index = int(url.split('opc.tcp://server-conso')[1][:1]) - 1
# DOCKERINFO = os.system("export DOCKERINFO=$(curl -s --unix-socket /run/docker.sock http://docker/containers/$HOSTNAME/json)")
'''
=======
>>>>>>> 98d968727ed992d67dfbcd2e59a82e9dfd5ac8b3
DOCKERINFO = os.popen("curl -s --unix-socket /run/docker.sock http://docker/containers/$HOSTNAME/json").read()
Name = json.loads(DOCKERINFO)["Name"].split("_")[1]
index = int(Name.split('server-conso')[1][:1])
'''

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
    elif (cpt in range (19,24)):
        consommation = random.uniform(1.02*consumption,1.34*consumption)
    return int(consommation)


async def main():
    _logger = logging.getLogger('asyncua')

    # server encryption  
<<<<<<< HEAD
    '''
    cert_user_manager = CertificateUserManager()
    await cert_user_manager.add_admin("certificates-all/certificate-scada-1.der", name='admin_scada')
    '''
=======
    cert_user_manager = CertificateUserManager()
    await cert_user_manager.add_admin("certificates-all/certificate-scada-1.der", name='admin_scada')
    await cert_user_manager.add_admin("/certificates-all/certificate-scada-rescue-1.der", name='admin_scada_rescue')


>>>>>>> 98d968727ed992d67dfbcd2e59a82e9dfd5ac8b3
    # setup our server
    consommation  = int(sys.argv[1])
    
    server = Server(user_manager=cert_user_manager)
    
    await server.init()
    server.set_endpoint('opc.tcp://0.0.0.0:4840/freeopcua/server/consommateur')

    # Security policy
    '''
    server.set_security_policy([ua.SecurityPolicyType.Basic256Sha256_SignAndEncrypt], permission_ruleset=SimpleRoleRuleset())
    '''

    # Load server certificate and private key.
<<<<<<< HEAD
    # This enables endpoints with signing and encryption.   
    '''
=======
    # This enables endpoints with signing and encryption.
>>>>>>> 98d968727ed992d67dfbcd2e59a82e9dfd5ac8b3
    await server.load_certificate(f"/certificates-all/certificate-conso-{index}.der")
    await server.load_private_key(f"private-key-conso-{index}.pem")
    '''

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
    async with server:
        while True:
            await asyncio.sleep(1)
            consommationHoraire = Consumption(cpt,consommation)
            print(f'consommationHoraire = {consommationHoraire}')
            await consommation1.write_value(consommationHoraire)
            cpt+=1
            if (cpt == 24):
                print ('Nouveau Jour')
                cpt = 0


if __name__ == '__main__':

    asyncio.run(main(), debug=False)
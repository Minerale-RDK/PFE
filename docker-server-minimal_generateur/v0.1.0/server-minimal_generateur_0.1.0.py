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

def Production(consommation, capacity):
    # Le réseau doit est stable à la fréquence f0=50Hz
    #f0 = int(50)
    # Ma production P varie en fonction de la journée
    production = consommation + random.uniform(0.75,1.04)
    if(production > capacity):
        production = capacity

    # f1 - f0 = (Production-Consommation) / Capacité Totale
    f1 = (production - consommation)/capacity + 50
    
    return f1

@uamethod
def func(parent, value):
    return value * 2

async def main():
    _logger = logging.getLogger('asyncua')

    # server encryption  
    cert_user_manager = CertificateUserManager()
    await cert_user_manager.add_admin("certificates/peer-certificate-client-scada-1.der", name='test_admin')

    # setup our server
    capacity  = int(sys.argv[1])
    server = Server(user_manager=cert_user_manager)
    await server.init()
    server.set_endpoint('opc.tcp://0.0.0.0:4840/freeopcua/server/')

    # Security policy  
    server.set_security_policy([ua.SecurityPolicyType.Basic256Sha256_SignAndEncrypt], permission_ruleset=SimpleRoleRuleset())

    # Load server certificate and private key.
    # This enables endpoints with signing and encryption.   
    await server.load_certificate("certificate-generateur.der")
    await server.load_private_key("privateKey.pem")

    ##DEBUG
    print("##DEBUG\n GENE produit {} W \n##### ".format(capacity))


    # setup our own namespace, not really necessary but should as spec
    uri = 'http://examples.freeopcua.github.io'
    idx = await server.register_namespace(uri)

    # populating our address space
    # server.nodes, contains links to very common nodes like objects and root
    objectFqandConso = await server.nodes.objects.add_object(idx, 'Freq&Prod')
    frequence = await objectFqandConso.add_variable(idx, 'frequence', ua.Variant(0, ua.VariantType.Double))
    consommation = await objectFqandConso.add_variable(idx, 'consommation', 0)
    # Set MyVariable to be writable by clients
    await consommation.set_writable()
    await server.nodes.objects.add_method(ua.NodeId('ServerMethod', 2), ua.QualifiedName('ServerMethod', 2), func, [ua.VariantType.Int64], [ua.VariantType.Int64])
    print('Starting server!')
    async with server:
        while True:
            await asyncio.sleep(1)
            newFreq = Production(await consommation.read_value(), capacity )
            print("nouvelle frequence = ", newFreq, "avec consommation", await consommation.read_value())
            await frequence.write_value(newFreq)


if __name__ == '__main__':

    asyncio.run(main(), debug=False)
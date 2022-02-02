import logging
import asyncio
import sys,os,json,math

from asyncua import ua, Server
from asyncua.common.methods import uamethod

import random

from asyncua.crypto.permission_rules import SimpleRoleRuleset
from asyncua.server.users import UserRole
from asyncua.server.user_managers import CertificateUserManager

DOCKERINFO = os.popen("curl -s --unix-socket /run/docker.sock http://docker/containers/$HOSTNAME/json").read()
Name = json.loads(DOCKERINFO)["Name"].split("_")[1]
index = int(Name.split('server-conso')[1][:1])


@uamethod
def func(parent, value):
    return value

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


allCerts=os.listdir("certificates-all")

def noNewCert():
    global allCerts
    if len(allCerts.copy()) == len(os.listdir("certificates-all")):
        return True
    else:
        print("########### new cert ###########")
        return False


async def main():
    _logger = logging.getLogger('asyncua')
    global allCerts

    # server encryption  
    cert_user_manager = CertificateUserManager()
    await cert_user_manager.add_admin("certificates-all/certificate-scada-1.der", name='admin_scada')
    await cert_user_manager.add_admin("certificates-all/certificate-scada-rescue-1.der", name='admin_scada_rescue')
    
    
    # setup our server
    consommation  = int(sys.argv[1])
    
    server = Server(user_manager=cert_user_manager)
    
    await server.init()
    server.set_endpoint('opc.tcp://0.0.0.0:4840/freeopcua/server/consommateur')

    # Security policy  
    server.set_security_policy([ua.SecurityPolicyType.Basic256Sha256_SignAndEncrypt], permission_ruleset=SimpleRoleRuleset())


    # Load server certificate and private key.
    # This enables endpoints with signing and encryption.
    await server.load_certificate(f"/certificates-all/certificate-conso-{index}.der")
    await server.load_private_key(f"private-key-conso-{index}.pem")


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
            if noNewCert():
                await asyncio.sleep(2)
                consommationHoraire = Consumption(cpt,consommation)
                print(f'consommationHoraire = {consommationHoraire}')
                await consommation1.write_value(consommationHoraire)
                cpt+=1
                if (cpt == 24):
                    print ('Nouveau Jour')
                    cpt = 0
            else:
                diff = list(set(allCerts).symmetric_difference(set(os.listdir('certificates-all'))))[0]
                name = diff.split("-")[1] + diff.split("-")[2][:-4]
                print(f"diff == {diff} && name == {name}")
                
                await cert_user_manager.add_admin(f"certificates-all/{diff}", name=f'admin_{name}')
                
                allCerts = os.listdir('certificates-all')




if __name__ == '__main__':

    asyncio.run(main(), debug=False)
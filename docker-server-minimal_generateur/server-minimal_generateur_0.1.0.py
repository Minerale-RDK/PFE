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

async def Production(consommation, capacity, coef_vitesse, production):

    productionAct = await production.read_value()

    if productionAct < consommation:
        productionAct += capacity*coef_vitesse         
        if productionAct > consommation:
            productionAct = consommation
        await production.write_value(int(productionAct))
    elif productionAct > consommation:
        productionAct -= capacity*coef_vitesse          
        if productionAct < consommation:
            productionAct = consommation
        await production.write_value(int(productionAct))
    else:
        print('teush')

    # f1 - f0 = (Production-Consommation) / Capacité Totale
    f1 = (productionAct - consommation)/capacity + 50
    #print(f"freq = {f1} productionAct={productionAct} consommation = {consommation} capacité = {capacity}")
    
    return f1


@uamethod
def func(parent, value):
    return value * 2

async def main():
    _logger = logging.getLogger('asyncua')

    # server encryption  
    cert_user_manager = CertificateUserManager()
    await cert_user_manager.add_admin("/certificates-all/certificate-scada-1.der", name='admin_scada')
    await cert_user_manager.add_admin("/certificates-all/certificate-capteur-1.der", name='admin_capteur')

    # setup our server
    capacity  = int(sys.argv[1]) #A changer avec type centrale qui va nous donner capacity et coeff vitesse
    server = Server(user_manager=cert_user_manager)
    await server.init()
    server.set_endpoint('opc.tcp://0.0.0.0:4840/freeopcua/server/')

    # Security policy  
    server.set_security_policy([ua.SecurityPolicyType.Basic256Sha256_SignAndEncrypt], permission_ruleset=SimpleRoleRuleset())

    # Load server certificate and private key.
    # This enables endpoints with signing and encryption.   
    await server.load_certificate("/certificates-all/certificate-gene-1.der")
    await server.load_private_key("private-key-gene-1.pem")

    ##DEBUG
    print("##DEBUG\n GENE produit {} W \n##### ".format(capacity))


    # setup our own namespace, not really necessary but should as spec
    uri = 'http://examples.freeopcua.github.io'
    idx = await server.register_namespace(uri)

    # populating our address space
    # server.nodes, contains links to very common nodes like objects and root

    objectCapaCoeff = await server.nodes.objects.add_object(idx, 'Capa&Coeff')
    capa = await objectCapaCoeff.add_variable(idx, 'capa', capacity)
    coeff = await objectCapaCoeff.add_variable(idx, 'coeff', 0.05)#Coeff en dur ici

    objectFqandProd = await server.nodes.objects.add_object(idx, 'Freq&Prod')
    production = await objectFqandProd.add_variable(idx, 'production', 0)
    frequence = await objectFqandProd.add_variable(idx, 'frequence', ua.Variant(0, ua.VariantType.Double))

    objectAlarm = await server.nodes.objects.add_object(idx, 'Alarm')
    alarmeFreq = await objectAlarm.add_variable(idx, 'alarme', 0)

    objectConso = await server.nodes.objects.add_object(idx, 'Consommation')   
    consommation = await objectConso.add_variable(idx, 'consommation', 0)
    
    objectRealConso = await server.nodes.objects.add_object(idx, 'Captor')
    realConsommation = await objectRealConso.add_variable(idx, 'realconso', 0)
    
    # Set MyVariable to be writable by clients
    await consommation.set_writable()
    await alarmeFreq.set_writable()
    await server.nodes.objects.add_method(ua.NodeId('ServerMethod', 2), ua.QualifiedName('ServerMethod', 2), func, [ua.VariantType.Int64], [ua.VariantType.Int64])
    await server.nodes.objects.add_method(ua.NodeId('ServerMethod2', 2), ua.QualifiedName('ServerMethod2', 2), func, [ua.VariantType.Double], [ua.VariantType.Double])
    print('Starting server!')
    async with server:
        start = True
        while True:
            while start:
                # await asyncio.sleep(0.5)
                # await asyncio.sleep(1.5)
                await asyncio.sleep(2.5)
                conso = await consommation.read_value()
                if conso == 0:
                    print("nouvelle frequence = ", await frequence.read_value(), "avec consommation", await consommation.read_value(), 'avec alarme = ', await alarmeFreq.read_value())
                    continue
                else:
                    await production.write_value(conso)
                    start = False
                    break
            # await asyncio.sleep(1)
            # await asyncio.sleep(2)
            await asyncio.sleep(4)
            
            newFreq = await Production(await consommation.read_value(), capacity, 0.05, production)
            if newFreq > 50.5:
                await alarmeFreq.write_value(1)
            if newFreq < 49.5:
                await alarmeFreq.write_value(-1)
            elif 49.5 <= newFreq <= 50.5:
                await alarmeFreq.write_value(0)           
            await frequence.write_value(newFreq)
            print("nouvelle frequence = ", await frequence.read_value(), "avec consommation", await consommation.read_value(), 'avec alarme = ', await alarmeFreq.read_value())
            
            # Conso Capteur
            await realConsommation.write_value(await consommation.read_value())  

import os 

if __name__ == '__main__':

    if not os.path.isfile("/certificates-all/certificate-gene-1.der"):
        cmd = ("openssl req -x509 -sha256 -nodes -days 365 -newkey rsa:2048 -config configuration_certs.cnf \
-keyout /private-key-gene-1.pem -outform der -out /certificates-all/certificate-gene-1.der")
        os.system(cmd)
    else:
        print("FILE EXISTS")

    asyncio.run(main(), debug=False)
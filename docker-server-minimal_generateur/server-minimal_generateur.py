import logging
import asyncio
import sys,os,json

from asyncua import ua, Server
from asyncua.common.methods import uamethod

from asyncua.crypto.permission_rules import SimpleRoleRuleset
from asyncua.server.users import UserRole
from asyncua.server.user_managers import CertificateUserManager

DOCKERINFO = os.popen("curl -s --unix-socket /run/docker.sock http://docker/containers/$HOSTNAME/json").read()
Name = json.loads(DOCKERINFO)["Name"].split("_")[1]
index = int(Name.split('server-gene')[1][:1])


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

    return f1


allCerts=os.listdir("certificates-all")

def noNewCert():
    global allCerts
    if len(allCerts.copy()) == len(os.listdir("certificates-all")):
        return True
    else:
        print("########### new cert ###########")
        return False

@uamethod
def func(parent, value):
    return value * 2

async def main():
    global allCerts
    _logger = logging.getLogger('asyncua')

    # server encryption
    
    cert_user_manager = CertificateUserManager()
    await cert_user_manager.add_admin("/certificates-all/certificate-scada-1.der", name='admin_scada')
    await cert_user_manager.add_admin("/certificates-all/certificate-scada-rescue-1.der", name='admin_scada_rescue')
    
    # setup our server
    capacity  = int(sys.argv[1])
    coefficient  = float(sys.argv[2])
    server = Server(user_manager=cert_user_manager)

    await server.init()
    server.set_endpoint('opc.tcp://0.0.0.0:4840/freeopcua/server/')

    # Security policy  
    
    server.set_security_policy([ua.SecurityPolicyType.Basic256Sha256_SignAndEncrypt], permission_ruleset=SimpleRoleRuleset())
    
    # Load server certificate and private key.
    # This enables endpoints with signing and encryption. 
      
    await server.load_certificate(f"/certificates-all/certificate-gene-{index}.der")
    await server.load_private_key(f"private-key-gene-{index}.pem")
    

    # setup our own namespace, not really necessary but should as spec
    uri = 'http://examples.freeopcua.github.io'
    idx = await server.register_namespace(uri)

    # populating our address space
    # server.nodes, contains links to very common nodes like objects and root
    objectCapaCoeff = await server.nodes.objects.add_object(idx, 'Capa&Coeff')
    capa = await objectCapaCoeff.add_variable(idx, 'capa', capacity)
    coeff = await objectCapaCoeff.add_variable(idx, 'coeff', coefficient)#Coeff en dur ici

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
            if noNewCert():
                while start:
                    await asyncio.sleep(0.5)
                    conso = await consommation.read_value()
                    if conso == 0:
                        print("nouvelle frequence = ", await frequence.read_value(), "avec consommation", await consommation.read_value(), 'avec alarme = ', await alarmeFreq.read_value())
                        continue
                    else:
                        await production.write_value(conso)
                        start = False
                        break
                await asyncio.sleep(1)
                
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

            else:
                diff = list(set(allCerts).symmetric_difference(set(os.listdir('certificates-all'))))[0]
                name = diff.split("-")[1] + diff.split("-")[2][:-4]
                print(f"diff == {diff} && name == {name}")
                
                await cert_user_manager.add_admin(f"certificates-all/{diff}", name=f'admin_{name}')
                
                allCerts = os.listdir('certificates-all')


if __name__ == '__main__':

    asyncio.run(main(), debug=False)
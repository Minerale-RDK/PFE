import logging
import asyncio
import sys
sys.path.insert(0, "..")

from asyncua import ua, Server
from asyncua.common.methods import uamethod

import random
import time
import math

starttime=time.time()

@uamethod
def func(parent, value):
    return value * 2


async def main():
    _logger = logging.getLogger('asyncua')
    # setup our server
    consommation  = int(sys.argv[1])
    server = Server()
    await server.init()
    server.set_endpoint('opc.tcp://0.0.0.0:4840/freeopcua/server/consommateur')

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
    async with server:
        while True:
            await asyncio.sleep(1)
            consommation +=1
            print("consommation cote consommateur ", consommation)
            await consommation1.write_value(consommation)



if __name__ == '__main__':

    asyncio.run(main(), debug=False)
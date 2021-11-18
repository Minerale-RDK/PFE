import random
import time
import math

starttime=time.time()

async def main():
    _logger = logging.getLogger('asyncua')
    # setup our server
    server = Server()
    await server.init()
    server.set_endpoint('opc.tcp://0.0.0.0:4840/freeopcua/server/')

    # setup our own namespace, not really necessary but should as spec
    uri = 'http://examples.freeopcua.github.io'
    idx = await server.register_namespace(uri)

    # populating our address space
    # server.nodes, contains links to very common nodes like objects and root
    myobj = await server.nodes.objects.add_object(idx, 'MyObject')
    myvar = await myobj.add_variable(idx, 'MyVariable', 6.7)
    # Set MyVariable to be writable by clients
    await myvar.set_writable()
    await server.nodes.objects.add_method(ua.NodeId('ServerMethod', 2), ua.QualifiedName('ServerMethod', 2), func, [ua.VariantType.Int64], [ua.VariantType.Int64])
    print('Starting server!')
    async with server:
        while True:
            await asyncio.sleep(1)
            frequence = random.uniform(49.45,50.55)
            time.sleep(1.0 - ((time.time() - starttime) % 1.0))
            new_val = frequence
            print('Set value of %s to %.1f', myvar, new_val)
            await myvar.write_value(new_val)


if __name__ == '__main__':

    #logging.basicConfig(level=logging.DEBUG)

    asyncio.run(main(), debug=False)
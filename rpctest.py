#!/usr/bin/python
#! -*- coding: utf8 -*-


from rpc_service.DjuderService import JudgerHandler

from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from random import randint


code = '''
def add():
    a, b = map(int, input().split())
    return a + b


if __name__ == '__main__':
    print(add())
'''


def main():
    # Make socket
    transport = TSocket.TSocket('localhost', 8080)

    # Buffering is critical. Raw sockets are very slow
    transport = TTransport.TBufferedTransport(transport)

    # Wrap in a protocol
    protocol = TBinaryProtocol.TBinaryProtocol(transport)

    # Create a client to use the protocol encoder
    client = JudgerHandler.Client(protocol)

    # Connect!
    transport.open()

    res = client.submit(str(randint(100000, 1000000)), '2', 'Python3', code, 'qq')
    
    # res = client.add('qq')
    
    print(res)

    # Close!
    transport.close()


if __name__ == '__main__':
    main()
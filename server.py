#!/usr/bin/python
#! -*- coding: utf8 -*-


from rpc_service.DjuderService import JudgerHandler
from judger import judge

from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer
from thrift.server import TProcessPoolServer
import os
import json


class DjudgerHandler:
    def __init__(self) -> None:
        pass    
    
    
    def submit(self, user, problem, language, code, info):
        res = judge(user=user, problem_id=problem, language=language, code=code)
        rst = json.dumps(res)
        return rst
    
    
    def add(self, cnf):
        return 99
    

if __name__ == '__main__':
    handler = DjudgerHandler()
    processor = JudgerHandler.Processor(handler)
    transport = TSocket.TServerSocket(host='127.0.0.1', port=8080)
    tfactory = TTransport.TBufferedTransportFactory()
    pfactory = TBinaryProtocol.TBinaryProtocolFactory()

    # server = TServer.TSimpleServer(processor, transport, tfactory, pfactory)

    # You could do one of these for a multithreaded server
    # server = TServer.TThreadedServer(
    #     processor, transport, tfactory, pfactory)
    # server = TServer.TThreadPoolServer(
    #     processor, transport, tfactory, pfactory)
    server = TProcessPoolServer.TProcessPoolServer(
        processor, transport, tfactory, pfactory)
    server.daemon = True
    print('Starting the server...')
    server.setNumWorkers(4)
    server.serve()
    print('done.')

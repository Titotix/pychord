from xmlrpc.server import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
import threading

class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/chord',)

class ChordServerxmlrpc(threading.Thread):
    def __init__(self, node, quiet=True):
        #TODO composition with threading.Thread rather than inheritance
        threading.Thread.__init__(self)
        self.ip = node.ip
        self.port = node.port
        self.node = node
        logReq = not quiet
        self.tcpserver = SimpleXMLRPCServer(
                (self.ip, self.port),
                allow_none=True,
                requestHandler=RequestHandler,
                logRequests=logReq
        )

    def run(self):
        #TODO only expose methods which should be used
        self.tcpserver.register_instance(self.node)
        self.tcpserver.serve_forever()

    def stop(self):
        self.tcpserver.shutdown()
        self.tcpserver.server_close()

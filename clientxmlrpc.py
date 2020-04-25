import xmlrpc.client

class ChordClientxmlrpcProxy(xmlrpc.client.ServerProxy):
    def __init__(self, ip, port):
        xmlrpc.client.ServerProxy.__init__(self,
                "http://{ip}:{port}/chord".format(ip=ip, port=port),
                allow_none=True
        )

def getXmlRPCClient(self, ip=None, port=None, node=None):
    """
    Create and return a ChordClientxmlrpcProxy

    @param ip: provided with port, creates a ServerProxy with those params
    @param port: provided with ip, creates a ServerProxy with those params
    @param node: creates a ServerProxy with node ip and port

    One of those params are mandatory : (ip and port) or (node)
    """
    if ip == port == node == None or\
            node == ip == None or\
            node == port == None:
        raise RunTimeError("Provide either ip and port or node")
    
    if isinstance(ip, str) and isinstance(port, int):
        return clientxmlrpc.ChordClientxmlrpcProxy(ip, port)
    elif isinstance(node, chord.BasicNode):
        return clientxmlrpc.ChordClientxmlrpcProx(node.ip, node.port)
    else:
        raise TypeError

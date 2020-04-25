import serverxmlrpc
import clientxmlrpc

from key import Key, Uid

class BasicNode(object):
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.uid = Uid(self.ip + ":" + repr(self.port))

    def getUid(self):
        return self.uid

class RemoteNode(BasicNode):
    def __init__(self, ip, port):
        BasicNode.__init__(self, ip, port)
        self.rpcProxy = clientxmlrpc.ChordClientxmlrpcProxy(ip, port)

class LocalNode(BasicNode):
    def __init__(self, ip, port):
        BasicNode.__init__(self, ip, port)
        self.successor = None

        self.server = serverxmlrpc.ChordServerxmlrpc(self)
        self.server.start()

    def stopXmlRPCServer(self):
        self.server.stop()

    def setsuccessor(self, successor):
        """
        Create a RemoteNode object and set to self.successor

        @param successor: dict with ip and port as key
        """
        self.successor = RemoteNode(successor["ip"], successor["port"])
    
    def addToRing(self, newnode):
        '''
        @param newnode : BasicNode to interact first with the ring
        '''
        if isinstance(newnode, dict):
            newnode = BasicNode(newnode["ip"], newnode["port"])
        if newnode.uid.value != self.uid.value:
            # TODO optim : no need to update all node of the ring at each new node
            self.updatesucc({"ip": newnode.ip, "port": newnode.port})
        else:

            raise Exception

    def updatesucc(self, newnode):
        #if newnode.uid.value == self.uid.value:
        #    raise Exception
        newnodeObj = BasicNode(newnode["ip"], newnode["port"])
        if self.successor is None:
            self.setsuccessor(newnode)
            self.successor.rpcProxy.setsuccessor({"ip":self.ip, "port":self.port})

        elif newnodeObj.uid.isbetween(self.uid.value, self.successor.uid.value):
            newnodeSuccip = self.successor.ip
            newnodeSuccport = self.successor.port
            self.setsuccessor(newnode)
            self.successor.rpcProxy.setsuccessor({"ip": newnodeSuccip, "port": newnodeSuccport})
        else:
            self.successor.rpcProxy.updatesucc(newnode)

    def lookupWithSucc(self, key):
        """
        Lookup method which uses only successor information
        Provided a key, lookupWithSucc return a dict with basic info
        about the responsible node of the provided key

        @param key: key to look for the responsible
        """
        if isinstance(key, Key):
            keyLookedUp = key
        elif isinstance(key, str):
            keyLookedUp = Key(key)
        else:
            raise TypeError

        # Self is successor ?
        if self.uid == keyLookedUp:
            return {"ip": self.ip, "port": self.port}
        # Is self.successor the successor of key ?
        if keyLookedUp.isbetween(self.uid.value, self.successor.uid.value):
            return {"ip": self.successor.ip, "port": self.successor.port}

        return self.successor.rpcProxy.lookupWithSucc(key)

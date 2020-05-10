import logging
import sys
import serverxmlrpc
import clientxmlrpc

from key import Key, Uid

log = logging.getLogger()
log.setLevel(logging.DEBUG)
ch = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter(' %(levelname)s - %(message)s')
ch.setFormatter(formatter)
log.addHandler(ch)

class BasicNode(object):
    def __init__(self, *args):
        """
        params are either ip and port OR a dict with keys ip and port 
        {"ip":<ip>, "port": <port>}
        """
        if len(args) == 2:
            ip = args[0]
            port = args[1]
        elif len(args) == 1:
            ip = args[0]["ip"]
            port = args[0]["port"]
        else:
            raise ValueError("len args of {} unsupported".format(len(args)))
        self.ip = ip
        self.port = port
        #TODO:optimization with sys.intern() str of 64 char
        self.uid = Uid(self.ip + ":" + repr(self.port))

    def getUid(self):
        return self.uid

    def asdict(self):
        """
        Creates and returns a dict with attr of the instance
        The dict can be used in rpc args
        """
        return {"ip": self.ip,
                "port": self.port,
                "uid": self.uid.value}

class NodeInterface(BasicNode):
    """
    Interface to call method on specified node
    When needed to use method from node N, N could be self.
    This class has the purpose  to abstract the choice of doing straightforward
    call on method if the node is self or to do RPC if it's a remote one

    If type of `arg` is LocalNode
    the NodeInterface object uses methods from it directly

    If type of `arg` is dict, we assume it is a remote node
    RPC will be done on arg["ip"] and arg["port"]
    (as a BasicNose is constructed from values of arg see BasicNode.__init__())

    @param arg: directly passed to BasicNode constructor
    """
    def __init__(self, arg):
        if isinstance(arg, LocalNode):
            super(NodeInterface, self).__init__(arg.ip, arg.port)
            self.methodProxy = arg
        elif isinstance(arg, dict):
            super(NodeInterface, self).__init__(arg)
            self.methodProxy = clientxmlrpc.ChordClientxmlrpcProxy(self.ip, self.port)
        else:
            raise TypeError("Supports LocalNode or dict")

class Finger(object):
    def __init__(self, key, originNode, respNode):
        """
        @param originNode
        @param respNode: dict or NodeInterface
        """
        if isinstance(originNode, LocalNode):
            self.originNode = originNode
        else:
            raise TypeError("originNode have to be LocalNode")

        #set key attr
        if isinstance(key, str):
            self.key = Key(key)
        elif isinstance(key, Key):
            self.key = key
        else:
            raise TypeError("key type not accepted. Support str and Key")

        self.setRespNode(respNode)

    def setRespNode(self, respNode):
        if isinstance(respNode, dict):
            self.respNode = self.originNode.getNodeInterface(respNode)
        elif isinstance(respNode, NodeInterface):
            self.respNode = respNode
        else:
            raise TypeError("Finger.setRespNode() accept dict and NodeInterface")

class LocalNode(BasicNode):
    def __init__(self, ip, port):
        BasicNode.__init__(self, ip, port)
        self.predecessor = NodeInterface(self)
        self.fingers = []
        self.createfingertable()

        self.server = serverxmlrpc.ChordServerxmlrpc(self)
        self.server.start()

    @property
    def successor(self):
        return self.fingers[0].respNode

    def asdict(self):
        return {"ip": self.ip,
                "port": self.port,
                "uid": self.uid.value,
                "succ": self.fingers[0].respNode.asdict(),
                "prede": self.predecessor.asdict()}

    def stopXmlRPCServer(self):
        self.server.stop()

    def createfingertable(self):
        """
        Create fingers table
        Calculate all fingerkey and initializze all to self
        """
        selfinterface = NodeInterface(self)
        for i in range(0, self.uid.idlength):
            self.fingers.append(Finger(self.calcfinger(i), self, selfinterface))

    def setsuccessor(self, successor):
        """
        Create a NodeInterface object and set to self.fingers[0].respnode
        which is also self.successor

        @param successor: dict with ip and port as key
        """
        self.fingers[0].setRespNode(self.getNodeInterface(successor))
    
    def setpredecessor(self, predecessor):
        """
        Create a NodeInterface object and set to self.predecessor

        @param predecessor: dict with ip and port as key
        """
        self.predecessor = self.getNodeInterface(predecessor)

    def getsuccessor(self):
        return self.fingers[0].respNode.asdict()

    def getpredecessor(self):
        return self.predecessor.asdict()

    def getNodeInterface(self, nodedict):
        """
        Return a NodeInterface object
        Compare self and nodedict to provide localNode or not
        """
        if nodedict["ip"] == self.ip and nodedict["port"] == self.port:
            return NodeInterface(self)
        else:
            return NodeInterface(nodedict)

    def addToRing(self, newnode):
        '''
        Outdated method
        @param newnode : BasicNode to interact first with the ring
        '''
        if isinstance(newnode, dict):
            newnode = BasicNode(newnode["ip"], newnode["port"])
        if newnode.uid.value != self.uid.value:
            # TODO optim : no need to update all node of the ring at each new node
            self.updatesucc(newnode.asdict())
            #self.updatefinger(newnode, self)
        else:

            raise Exception

    def updatesucc(self, newnode):
        """
        Outdated method
        Update successor with the node wich just join if relevant
        If not, propagate updatesucc to its own successor
        """
        newnodeObj = BasicNode(newnode["ip"], newnode["port"])

        #TODO: check if this can happen and in wich case
        # as it should not happen if updatesucc work as expected
        if newnode.uid.value == self.uid.value:
            raise Exception

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

    def join(self, node):
        self.init_fingers(node)
        self.update_others()

    def init_fingers(self, existingnode):
        log.debug("%s - init_fingers with %s" %(self.uid, existingnode.uid))
        fingerkey = self.fingers[0].key
        self.setsuccessor(existingnode.methodProxy.find_successor(fingerkey))
        self.setpredecessor(self.fingers[0].respNode.methodProxy.getpredecessor())
        self.predecessor.methodProxy.setsuccessor(self.asdict()) # added compare to paper
        self.fingers[0].respNode.methodProxy.setpredecessor(self.asdict())
        for i in range(0, self.uid.idlength - 1):
            if self.fingers[i + 1].key.isbetween(self.fingers[i].key, self.fingers[i].respNode.uid): #changed from paper's algo which use self.uid in place of fingers[I].key
                self.fingers[i + 1].setRespNode(self.fingers[i].respNode)
            else:
                nextfingersucc = existingnode.methodProxy.find_successor(
                        self.fingers[i+1].key)
                self.fingers[i+1].setRespNode(nextfingersucc)

    def update_others(self):
        for i in range(0, self.uid.idlength):
            log.debug("%s - update_others for i=%i" %(self.uid, i))
            predenode = self.find_predecessor(self.uid - pow(2, i))
            self.getNodeInterface(predenode).methodProxy.update_finger_table(self.asdict(), i)

    def update_finger_table(self, callingnode, i):
        callingnode = BasicNode(callingnode)
        #update_finger_table looped over the ring and came back to self
        if callingnode.uid == self.uid:
            return
        log.debug("%s - update_finger_table with node '%s' for i=%i" %(self.uid, callingnode.uid, i))
        #TODO check if key and node uid of the same finger could be equal and then lead to a exception in isbetween
        if callingnode.uid.isbetween(self.fingers[i].key, self.fingers[i].respNode.uid):
            log.debug("%s - update_finger_table:  callingnode uid is between self.uid and fingers(%i). node.uid" %(self.uid, i))
            self.fingers[i].setRespNode(callingnode.asdict())
            #TODO optim : self knows fingers[i] uid so it can calculate if predecessor has chance or not to have to update his finger(i)
            if self.predecessor.uid != callingnode.uid: # dont rpc on callingnode it self
                self.predecessor.methodProxy.update_finger_table(callingnode.asdict(), i)

    def find_successor(self, key):
        """
        Lookup method for successor of key
        Use predecessor, successor and fingers information
        Should produce the same answer than lookupWithSucc
        """
        if isinstance(key, dict):
            key = key["value"]
        prednode = self.find_predecessor(key)
        #TODO: avoird rpc to it self in case predkey is actually self
        #if self.ip != predkey["ip"] or self.ip == predkey["ip"] and self.port != predkey["port"]:
        return prednode["succ"]

    def find_predecessor(self, key):
        if isinstance(key, dict):
            key = key["value"]
        key = Key(key)
        log.debug("%s - find_predecessor for '%s'" %(self.uid, key.value))
        if self.uid == self.fingers[0].respNode.uid:
            return self.asdict()
        if key.isbetween(self.uid, self.fingers[0].respNode.uid):
            return self.asdict()
        #TODO IDEA maybe: overwrite dispatch on xmlrpc server
        # then it is possible to dispatch on specific method for rpc
        # so in the next line case we are not force to transform cloPrecedFinger into a NodeInterface
        #TODO avoid casting directly in NodeInterface because we loose potential succ/prede info from the original dict
        cloPrecedFinger= self.getNodeInterface(self.closest_preceding_finger(key.value))
        cloPrecedFingerSucc = BasicNode(cloPrecedFinger.methodProxy.getsuccessor())
        #TODO add uid info to return dict of rpc
        if cloPrecedFinger.uid == cloPrecedFingerSucc.uid:
            #TODO Here, self noticed that node has wrong fingers, should I correct it ?
            resdict = cloPrecedFinger.asdict()
            resdict["succ"] = cloPrecedFingerSucc.asdict()
            return resdict
        while not key.isbetween(cloPrecedFinger.uid, cloPrecedFingerSucc.uid):
            cloPrecedFingerDict = cloPrecedFinger.methodProxy.closest_preceding_finger(key.value)
            if hasattr(cloPrecedFingerDict, "succ"):
                #TODO in test, is this if usefull ?
                breakpoint() #probably not...
                cloPrecedFingerSucc = self.getNodeInterface(cloPrecedFingerDict["succ"])
            else:
                cloPrecedFinger = self.getNodeInterface(cloPrecedFingerDict)
                if cloPrecedFinger.uid == self.uid:
                    cloPrecedFingerSucc = BasicNode(self.getsuccessor())
                else:
                    cloPrecedFingerSucc = BasicNode(cloPrecedFinger.methodProxy.getsuccessor())
        resdict = cloPrecedFinger.asdict()
        resdict["succ"] = cloPrecedFingerSucc.asdict()
        return resdict

    def closest_preceding_finger(self, keyvalue):
        for i in range(self.uid.idlength - 1, -1, -1):
            #TODO aggregate all usecase of isbetween and handle genericly the limit1 == limit2 exception ?
            if self.uid == keyvalue:
                #TODO I DONT KNOW what to do!!!
                continue
            if self.fingers[i].respNode.uid == self.uid: # (1)
                if self.successor.uid == self.uid:
                    return self.asdict() #self is alone on the ring
                if Key(keyvalue).isbetween(self.uid, self.successor.uid):
                    return self.asdict()
                continue
            if self.fingers[i].respNode.uid.isbetween(self.uid, keyvalue): # change from papaer algo: fingers[i].key in place of self.uid
                return self.fingers[i].respNode.asdict()
        return self.asdict() # Should not happen because of (1), not sure sought

    def updatefinger(self, firstnode):
        '''
        Update finger table
        Dummy update wich loookup all fingerkey
        When finished, propagate updatefinger to all node of the ring
        /!\ Very costly in rpc /!\
        finger is an array of dict {resp, key}
            `resp` is the Node responsible for `key`
        @param firstnode: node which launch the update
        '''
        for i in range(0, self.uid.idlength):
            resp = self.lookupWithSucc(self.fingers[i].key)
            self.fingers[i].setRespNode(resp)
        if firstnode.uid != self.fingers[0].respNode.uid:
            self.fingers[0].respNode.methodProxy.updatefinger(firstnode)

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

        return self.successor.methodProxy.lookupWithSucc(key)

    def calcfinger(self, k):
        '''
        Returns computed key for finger k
        @param k: from 0 to (m - 1)
        '''
        if k > self.uid.idlength - 1:
            raise ValueError("calcfinger: value above {} are not accepted".format(self.idlength))
        return self.uid + pow(2, k)

    def printFingers(self):
        for n, f in enumerate(self.fingers):
            print("TABLE: finger{0} : "
                "- key: {2} - resp: {1}"
                .format(n, f.node.uid, f.key))
            #if f["resp"].uid.value != self.lookupfinger(n, useOnlySucc=True).uid.value:
                #self.log.error("error between finger table and computed value")
                #continue

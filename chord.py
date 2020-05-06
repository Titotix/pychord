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

        # self.logging
        #TODO This self.log sucks
        #self.log = logging.getLogger(repr(self.uid))
        #self.log.setLevel(logging.INFO)
        #ch = logging.StreamHandler(sys.stdout)
        #ch.setLevel(logging.DEBUG)
        #formatter = logging.Formatter('%(levelname)s - %(name)s - %(message)s')
        #ch.setFormatter(formatter)
        #self.log.addHandler(ch)

        #self.log.debug("node creation: uid={}".format(self.uid.value))

    #def __repr__(self):
    #    #TODO: no hardcoded class name
    #    return "<class BasicNode - {hash}>".format(hash=self.uid)

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

class RemoteNode(BasicNode):
    def __init__(self, *args):
        super(RemoteNode, self).__init__(*args)
        self.rpcProxy = clientxmlrpc.ChordClientxmlrpcProxy(self.ip, self.port)

class Finger(object):
    def __init__(self, key, respnode):
        #set key attr
        if isinstance(key, str):
            self.key = Key(key)
        elif isinstance(key, Key):
            self.key = key
        else:
            raise TypeError("key type not accepted. Support str and Key")

        # self.node can be either RemoteNode or LocalNode
        # according to who's node is it
        #TODO: find a way to abstract access to node's method wether it's Remote or not
        self.setnode(respnode)

    def setnode(self, node):
        if isinstance(node, dict):
            self.node = RemoteNode(node["ip"], node["port"])
        elif isinstance(node, BasicNode):
            self.node = RemoteNode(node.ip, node.port)
        elif isisntance(node, RemoteNode):
            self.node = node
        else:
            raise TypeError("Finger.setnode() accept dict, BasicNode or RemoteNode")

class LocalNode(BasicNode):
    def __init__(self, ip, port):
        BasicNode.__init__(self, ip, port)
        self.predecessor = BasicNode(self.ip, self.port)
        self.fingers = []
        self.createfingertable()

        self.server = serverxmlrpc.ChordServerxmlrpc(self)
        self.server.start()

    @property
    def successor(self):
        return self.fingers[0].node

    def asdict(self):
        return {"ip": self.ip,
                "port": self.port,
                "uid": self.uid.value,
                "succ": self.fingers[0].node.asdict(),
                "prede": self.predecessor.asdict()}

    def stopXmlRPCServer(self):
        self.server.stop()

    def createfingertable(self):
        """
        Create fingers table
        Calculate all fingerkey and initializze all to self
        """
        node = BasicNode(self.ip, self.port)
        for i in range(0, self.uid.idlength):
            self.fingers.append(Finger(self.calcfinger(i), node))

    def setsuccessor(self, successor):
        """
        Create a RemoteNode object and set to self.successor

        @param successor: dict with ip and port as key
        """
        self.fingers[0].setnode(RemoteNode(successor["ip"], successor["port"]))
    
    def setpredecessor(self, predecessor):
        """
        Create a RemoteNode object and set to self.predecessor

        @param predecessor: dict with ip and port as key
        """
        self.predecessor = RemoteNode(predecessor["ip"], predecessor["port"])

    def getsuccessor(self):
        return self.fingers[0].node.asdict()

    def getpredecessor(self):
        return self.predecessor.asdict()

    def addToRing(self, newnode):
        '''
        Outdated method
        @param newnode : BasicNode to interact first with the ring
        '''
        if isinstance(newnode, dict):
            newnode = BasicNode(newnode["ip"], newnode["port"])
        #self.log.debug("{} want to join {}".format(newnode.uid.value, self.uid.value))
        if newnode.uid.value != self.uid.value:
            # TODO optim : no need to update all node of the ring at each new node
            self.updatesucc(newnode.asdict())
            #self.updatefinger(newnode, self)
        else:

            #self.log.error("Same uid than contacted node")
            raise Exception

    def updatesucc(self, newnode):
        """
        Outdated method
        """
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

    def join(self, node):
        self.init_fingers(node)
        self.update_others()

    def init_fingers(self, existingnode):
        log.debug("%s - init_fingers with %s" %(self.uid, existingnode.uid))
        fingerkey = self.fingers[0].key
        self.setsuccessor(existingnode.rpcProxy.find_successor(fingerkey))
        self.setpredecessor(self.fingers[0].node.rpcProxy.getpredecessor())
        self.predecessor.rpcProxy.setsuccessor(self.asdict()) # added compare to paper
        self.fingers[0].node.rpcProxy.setpredecessor(self.asdict())
        for i in range(0, self.uid.idlength - 1):
            if self.fingers[i + 1].key.isbetween(self.fingers[i].key, self.fingers[i].node.uid): #changed from paper's algo which use self.uid in place of fingers[I].key
                self.fingers[i + 1].setnode(self.fingers[i].node)
            else:
                nextfingersucc = existingnode.rpcProxy.find_successor(
                        self.fingers[i+1].key)
                self.fingers[i+1].setnode(nextfingersucc)

    def update_others(self):
        for i in range(0, self.uid.idlength):
            log.debug("%s - update_others for i=%i" %(self.uid, i))
            predenode = self.find_predecessor(self.uid - pow(2, i))
            RemoteNode(predenode).rpcProxy.update_finger_table(self.asdict(), i)

    def update_finger_table(self, callingnode, i):
        callingnode = BasicNode(callingnode)
        #update_finger_table looped over the ring and came back to self
        if callingnode.uid == self.uid:
            return
        log.debug("%s - update_finger_table with node '%s' for i=%i" %(self.uid, callingnode.uid, i))
        #TODO check if key and node uid of the same finger could be equal and then lead to a exception in isbetween
        if callingnode.uid.isbetween(self.fingers[i].key, self.fingers[i].node.uid):
            log.debug("%s - update_finger_table:  callingnode uid is between self.uid and fingers(%i). node.uid" %(self.uid, i))
            self.fingers[i].setnode(callingnode)
            #TODO optim : self knows fingers[i] uid so it can calculate if predecessor has chance or not to have to update his finger(i)
            if self.predecessor.uid != callingnode.uid: # dont rpc on callingnode it self
                self.predecessor.rpcProxy.update_finger_table(callingnode.asdict(), i)

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
        if self.uid == self.fingers[0].node.uid:
            return self.asdict()
        if key.isbetween(self.uid, self.fingers[0].node.uid):
            return self.asdict()
        #TODO IDEA maybe: overwrite dispatch on xmlrpc server
        # then it is possible to dispatch on specific method for rpc
        # so in the next line case we are not force to transform cloPrecedFinger into a RemoteNode
        #TODO avoid casting directly in RemoteNode because we loose potential succ/prede info from the original dict
        cloPrecedFinger= RemoteNode(self.closest_preceding_finger(key.value))
        cloPrecedFingerSucc = BasicNode(cloPrecedFinger.rpcProxy.getsuccessor())
        #TODO add uid info to return dict of rpc
        if cloPrecedFinger.uid == cloPrecedFingerSucc.uid:
            #TODO Here, self noticed that node has wrong fingers, should I correct it ?
            resdict = cloPrecedFinger.asdict()
            resdict = resdict["succ"] = cloPrecedFingerSucc.asdict()
            return resdict
        while not key.isbetween(cloPrecedFinger.uid, cloPrecedFingerSucc.uid):
            cloPrecedFingerDict = cloPrecedFinger.rpcProxy.closest_preceding_finger(key.value)
            if hasattr(cloPrecedFingerDict, "succ"):
                #TODO in test, is this if usefull ?
                breakpoint() #probably not...
                cloPrecedFingerSucc = RemoteNode(cloPrecedFingerDict["succ"])
            else:
                cloPrecedFinger = RemoteNode(cloPrecedFingerDict)
                #TODO abstract routing if RemoteNode is actually self do not RPC call method before rpcProxy ?
                if cloPrecedFinger.uid == self.uid:
                    cloPrecedFingerSucc = BasicNode(self.getsuccessor())
                else:
                    cloPrecedFingerSucc = BasicNode(cloPrecedFinger.rpcProxy.getsuccessor())
        resdict = cloPrecedFinger.asdict()
        resdict["succ"] = cloPrecedFingerSucc.asdict()
        return resdict

    def closest_preceding_finger(self, keyvalue):
        for i in range(self.uid.idlength - 1, -1, -1):
            #TODO aggregate all usecase of isbetween and handle genericly the limit1 == limit2 exception ?
            if self.uid == keyvalue:
                #TODO I DONT KNOW what to do!!!
                continue
            if self.fingers[i].node.uid == self.uid: # (1)
                if self.successor.uid == self.uid:
                    return self.asdict() #self is alone on the ring
                if Key(keyvalue).isbetween(self.uid, self.successor.uid):
                    return self.asdict()
                continue
            if self.fingers[i].node.uid.isbetween(self.uid, keyvalue): # change from papaer algo: fingers[i].key in place of self.uid
                return self.fingers[i].node.asdict()
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
            self.fingers[i].setnode(resp)
        if firstnode.uid != self.fingers[0].node.uid:
            self.fingers[0].node.rpcProxy.updatefinger(firstnode)

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

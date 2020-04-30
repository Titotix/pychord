import logging
import sys
import serverxmlrpc
import clientxmlrpc

from key import Key, Uid

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
    
    def addToRing(self, newnode):
        '''
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

    def updatefinger(self, newnode, firstnode):
        '''
        UPdate finger table for all ring in a clockwise around successor fashion
        finger is an array of dict {resp, key}
            `resp` is the Node responsible for `key`
        @param newnode: new node which imply this update
        @param firstnode: node which launch the update
        '''
        for i in range(0, self.uid.idlength):
            fingerkey = self.calcfinger(i)
            resp = self.lookupWithSucc(fingerkey)
            self.finger[i] = {"resp": resp, "key": Key(fingerkey)}
            #self.finger[i] = self.lookupfinger(i, useOnlySucc=True)
        if firstnode is not self.successor:
            self.successor.updatefinger(newnode, firstnode)

    def lookupfinger(self, k, useOnlySucc=False):
        '''
        Returns the node responsible for finger k
        @param m: Id length of the ring. (m = Key.idlength)
            Ring is constituted of 2^m nodes maximum
        '''
        if useOnlySucc:
            return self.lookupWithSucc(self.calcfinger(k))
        else:
            return self.lookup(self.calcfinger(k))


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

    def lookup(self, key):
        """
        Lookup method to find the responsive node for a given key

        return a node object
        
        """
        #TODO not working on test done 20-04-2020
        
        if isinstance(key, BasicNode):
            key = node.uid
        elif isinstance(key, Key):
            key = key
        elif isinstance(key, str):
            key = Key(key)
        else:
            raise TypeError

        def getNextDichotomy(prevDichotomy, dichotomy, sign):
            fingmax = self.uid.idlength - 1
            fingmin = 0
            if prevDichotomy == dichotomy:
                raise ValueError("prevDichotomy & dichotomy are eq")
            if sign not in ["+", "-"]:
                raise Exception("getNetxtDichotomy used with invalid sign")
            elif sign == "+":
                if prevDichotomy < dichotomy:
                    return dichotomy + ((nfinger - dichotomy) // 2)
                else:
                    return dichotomy + ((prevDichotomy - dichotomy) // 2)
            elif sign == "-":
                if prevDichotomy < dichotomy:
                    return dichotomy - ((dichotomy - prevDichotomy) // 2)
                else:
                    return dichotomy - (dichotomy // 2)

        nfinger = self.uid.idlength
        fingmax = nfinger - 1

        # test if key to lookup is outside of finger tables
        if key.isbetween(self.finger[fingmax]["resp"].uid + 1,
                         self.finger[0]["key"] - 1):
            # let's ask to last finger
            #self.log.debug("lookup recurse to node {}".format(self.finger[fingmax]["resp"]))
            return self.finger[fingmax]["resp"].lookup(key)

        #self.log.debug("key={}; finger(255)[resp]={}; finger(0)(key)={}\nfinger(255)(key)={}"
        #               .format(key,
        #                       Key(self.finger[fingmax]["resp"].uid + 1),
        #                       Key(self.finger[0]["key"] - 1),
        #                       self.finger[255]["key"])
        #              )
        # self knows the answer because key < (self finger max)

        dichotomy = nfinger // 2
        prevDichotomy = 0
        # algorithm by dichotomy
        while True:

            # finger(0) <= key < finger(dichotomy)
            # finger(dichotomy)[key] <= key <= finger(dichotomy)[resp]
            if key.isbetween(self.finger[dichotomy]["key"],
                               self.finger[dichotomy]["resp"].uid.value):
                #self.log.debug("Assigns {} as succ for {}"
                #        .format(self.finger[dichotomy]["resp"], key))
                return self.finger[dichotomy]["resp"]

            elif key.isbetween(self.finger[0]["key"] + 1,
                             self.finger[dichotomy]["key"] - 1):
                #self.log.debug("key down to dichotomy: dichotomy:{} -"
                #               "prevDichotomy:{} -"
                #               "finger-dicho)(res)={} -"
                #               "finger-dicho)(key)={} -"
                #               "finger(0)[keyt]={}"
                #               .format(dichotomy,
                #                       prevDichotomy,
                #                       self.finger[dichotomy]["resp"],
                #                       self.finger[dichotomy]["key"],
                #                       self.finger[0]["key"]))

                if self.finger[dichotomy - 1]["resp"] != self.finger[dichotomy]["resp"]:
                    if key.isbetween(self.finger[dichotomy - 1]["resp"].uid + 1,
                                   self.finger[dichotomy]["key"] - 1):
                        return self.finger[dichotomy - 1]["resp"].lookup(key)
                try:
                    dichotomy_tmp = getNextDichotomy(prevDichotomy,
                                                     dichotomy,
                                                     "-")
                except ValueError as e:
                    #self.log.error(e)
                    raise
                prevDichotomy = dichotomy
                dichotomy = dichotomy_tmp

            # finger(dichotomy) < key <= finger(255)
            elif key.isbetween(self.finger[dichotomy]["resp"].uid + 1,
                               self.finger[fingmax]["resp"].uid.value):
                #self.log.debug("UP to dichotomy: dichotomy:{} -"
                #               "prevDichotomy:{} -"
                #               "finger-dicho(resp)={} -"
                #               "finger(0)[key]={} - "
                #               "finger(dichotomy-1)[resp]={} -"
                #               "finger(dicho)[key]={}"
                #               .format(dichotomy,
                #                       prevDichotomy,
                #                       self.finger[dichotomy]["resp"],
                #                       self.finger[0]["key"],
                #                       self.finger[dichotomy - 1]["resp"].uid,
                #                       self.finger[dichotomy]["key"],
                #                       ))

                # if finger dicho and next finger does not have same responsible
                # it means there is a room for unreferenced node in self fingers
                # if looked up key is in this room, we have to ask to the finger dichotomy
                # to lookup for self, as self does not know the answer
                if self.finger[dichotomy + 1]["resp"] != self.finger[dichotomy]["resp"]:
                    # test if key is in this room
                    # between the finger dichotomy responsible & the next finger key
                    if key.isbetween(self.finger[dichotomy]["resp"].uid + 1,
                                     self.finger[dichotomy + 1]["key"] - 1):
                        # let's ask to self.finger[dichotomy]
                        return self.finger[dichotomy]["resp"].lookup(key)
                try:
                    dichotomy_tmp = getNextDichotomy(prevDichotomy,
                                                     dichotomy,
                                                     "+")
                except ValueError as e:
                    #self.log.error(e)
                    raise

                prevDichotomy = dichotomy
                dichotomy = dichotomy_tmp

            else:
                #self.log.error("OUT OF TOWN")
                raise IndexError("lookup failed on properly catching the inclusion of the key.")

 
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

    def printRing(self):
        succ = self.successor
        output = "Ring from {}]:\n".format(self.uid.value)
        key = self.successor.uid
        while key != self.uid:
            output += repr(key) + " -> "
            succ = succ.successor
            key = succ.uid
        #self.log.debug(output)


import logging
import sys
import threading
from xmlrpc.server import SimpleXMLRPCServer

from key import Key, Uid

def iseven(value):
    return value % 2 == 0


# perhaps inherit from Node ? #TODO
#class ThreadServerRPC(threading.Thread):
#    def __init__(self, node):
#        threading.Thread.__init__(self)
#        self.node = node
#        self.simplexmlrpcserver = SimpleXMLRPCServer((self.node.ip, self.node.port),
#                                                     allow_none=True)
#        self.simplexmlrpcserver.register_instance(self.node)
#
#        # if daemon si True, threadd will exit with launcher THread, main one for now
#        self.daemon = True
#
#    def run(self):
#        self.simplexmlrpcserver.serve_forever()

class Node(object):
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.uid = Uid(self.ip + ":" + repr(self.port))
        self.successor = self
        # TODO create a finger class & integrate
        self.finger = []
        self.initfinger()

        # self.logging
        self.log = logging.getLogger(repr(self.uid))
        self.log.setLevel(logging.DEBUG)
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(levelname)s - %(name)s - %(message)s')
        ch.setFormatter(formatter)
        self.log.addHandler(ch)

        #self.threadserverrpc = ThreadServerRPC(self)
        #self.threadserverrpc.start()
        # WIP
        # ThreadServerRPC(self).start()
        self.log.debug("node creation: uid={}".format(self.uid.value))

    def __repr__(self):
        return "<class Node - {hash}>".format(hash=self.uid)

    def initfinger(self):
        for i in range(0, self.uid.idlength):
            self.finger.append(None)

    def setsuccessor(self, successor):
        self.successor = successor
    
    def addToRing(self, newnode):
        '''
        @param newnode : Node to interact first with the ring
        '''
        self.log.debug("{} want to join {}".format(newnode.uid.value, self.uid.value))
        if newnode.uid.value != self.uid.value:
            # TODO optim : no need to update all node of the ring at each new node
            self.updatesucc(newnode)
            self.updatefinger(newnode, self)
        else:

            self.log.error("Same uid than contacted node")
            raise Exception

    def updatesucc(self, newnode):
        if newnode.uid.value == self.uid.value:
            raise Exception
        if self == self.successor:
            self.setsuccessor(newnode)
            newnode.setsuccessor(self)
        
        elif newnode.uid.isbetween(self.uid.value, self.successor.uid.value):
            newnode.setsuccessor(self.successor)
            self.setsuccessor(newnode)
        else:
            self.successor.updatesucc(newnode)

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
            resp = self.lookup(fingerkey, useOnlySucc=True)
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
        return self.lookup(self.calcfinger(k), useOnlySucc)

            
    def lookup(self, key, useOnlySucc=False):
        
        if isinstance(key, Node):
            key = node.uid
        elif isinstance(key, Key):
            key = key
        elif isinstance(key, str):
            key = Key(key)
        else:
            raise Exception

        def getNextDichotomy(prevDichotomy, dichotomy, sign):
            fingmax = self.uid.idlength - 1
            fingmin = 0
            if prevDichotomy == dichotomy:
                raise ValueError("prevDichotomy & dichotomy are eq")
            if sign not in ["+", "-"]:
                raise Exception("getNetxtDichotomy used with invalid sign")
            elif sign is "+":
                if prevDichotomy < dichotomy:
                    return dichotomy + ((nfinger - dichotomy) // 2)
                else:
                    return dichotomy + ((prevDichotomy - dichotomy) // 2)
            elif sign is "-":
                if prevDichotomy < dichotomy:
                    return dichotomy - ((dichotomy - prevDichotomy) // 2)
                else:
                    return dichotomy - (dichotomy // 2)

        # lookup on successor and then ask to the successor
        if useOnlySucc:
            # Self is successor ?
            if self.uid == key:
                return self
            # Is self.successor the successor of key ? 
            if key.isbetween(self.uid.value, self.successor.uid.value):
                return self.successor
            
            return self.successor.lookup(key, useOnlySucc)

        # Use finger table to optim lookup
        else:

            nfinger = self.uid.idlength
            fingmax = nfinger - 1

            # test if key to lookup is outside of finger tables
            if key.isbetween(self.finger[fingmax]["resp"].uid + 1,
                             self.finger[0]["key"] - 1):
                # let's ask to last finger
                self.log.debug("lookup recurse to node {}".format(self.finger[fingmax]["resp"]))
                return self.finger[fingmax]["resp"].lookup(key, useOnlySucc)

            self.log.debug("key={}; finger(255)[resp]={}; finger(0)(key)={}\nfinger(255)(key)={}"
                           .format(key,
                                   Key(self.finger[fingmax]["resp"].uid + 1),
                                   Key(self.finger[0]["key"] - 1),
                                   self.finger[255]["key"])
                          )
            # self knows the answer because key < (self finger max)

            dichotomy = nfinger // 2
            prevDichotomy = 0
            # algorithm by dichotomy
            while True:

                # finger(0) <= key < finger(dichotomy)
                # finger(dichotomy)[key] <= key <= finger(dichotomy)[resp]
                if key.isbetween(self.finger[dichotomy]["key"],
                                   self.finger[dichotomy]["resp"].uid.value):
                    self.log.debug("Assigns {} as succ for {}"
                            .format(self.finger[dichotomy]["resp"], key))
                    return self.finger[dichotomy]["resp"]
                    
                elif key.isbetween(self.finger[0]["key"] + 1,
                                 self.finger[dichotomy]["key"] - 1):
                    self.log.debug("key down to dichotomy: dichotomy:{} -"
                                   "prevDichotomy:{} -"
                                   "finger-dicho)(res)={} -"
                                   "finger-dicho)(key)={} -"
                                   "finger(0)[keyt]={}"
                                   .format(dichotomy,
                                           prevDichotomy,
                                           self.finger[dichotomy]["resp"],
                                           self.finger[dichotomy]["key"],
                                           self.finger[0]["key"]))

                    if self.finger[dichotomy - 1]["resp"] != self.finger[dichotomy]["resp"]:
                        if key.isbetween(self.finger[dichotomy - 1]["resp"].uid + 1,
                                       self.finger[dichotomy]["key"] - 1):
                            return self.finger[dichotomy - 1]["resp"].lookup(key, useOnlySucc)
                    try:
                        dichotomy_tmp = getNextDichotomy(prevDichotomy,
                                                         dichotomy,
                                                         "-")
                    except ValueError as e:
                        self.log.error(e)
                        raise
                    prevDichotomy = dichotomy
                    dichotomy = dichotomy_tmp

                # finger(dichotomy) < key <= finger(255)
                elif key.isbetween(self.finger[dichotomy]["resp"].uid + 1,
                                   self.finger[fingmax]["resp"].uid.value):
                    self.log.debug("UP to dichotomy: dichotomy:{} -"
                                   "prevDichotomy:{} -"
                                   "finger-dicho(resp)={} -"
                                   "finger(0)[key]={} - "
                                   "finger(dichotomy-1)[resp]={} -"
                                   "finger(dicho)[key]={}"
                                   .format(dichotomy,
                                           prevDichotomy,
                                           self.finger[dichotomy]["resp"],
                                           self.finger[0]["key"],
                                           self.finger[dichotomy - 1]["resp"].uid,
                                           self.finger[dichotomy]["key"],
                                           ))

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
                            return self.finger[dichotomy]["resp"].lookup(key, useOnlySucc)
                    try:
                        dichotomy_tmp = getNextDichotomy(prevDichotomy,
                                                         dichotomy,
                                                         "+")
                    except ValueError as e:
                        self.log.error(e)
                        raise

                    prevDichotomy = dichotomy
                    dichotomy = dichotomy_tmp

                else:
                    self.log.error("OUT OF TOWN")
                    raise IndexError("lookup failed on properly catching the inclusion of the key.")

 
    def calcfinger(self, k):
        '''
        Returns computed key for finger k
        @param k: from 0 to (m - 1)
        '''
        return self.uid + pow(2, k)

    def printFingers(self):
        for n, f in enumerate(self.finger):
            self.log.debug("TABLE: finger{0} : "
                "- key: {2} - resp: {1}"
                .format(n, f["resp"].uid, f["key"]))
            if f["resp"].uid.value != self.lookupfinger(n, useOnlySucc=True).uid.value:
                self.log.error("error between finger table and computed value")

    def printRing(self):
        succ = self.successor
        output = "Ring from {}]:\n".format(self.uid.value)
        key = self.successor.uid
        while key != self.uid:
            output += repr(key) + " -> "
            succ = succ.successor
            key = succ.uid
        self.log.debug(output)


import SocketServer
import logging
import hashlib
import socket
import math


class Key(object):

    def __init__(self, value):
        self.value = value

    def getValue(self, value):
        self.value = self.hash(value).hexdigest()
 
    def sum(self, value):
        raise NotImplementedError 
    
    # TODO optim : each between call will be a RPC, sad if we locally know the value of remote node ?
    def isbetween(self, limit1, limit2):
        '''
        Returns True if self.value is inside [limit1,  limit2]
        Raise exception if limit1 == limit2
        '''
        if len(self.value) != len(limit1) != len(limit2):
            #self.log.error("Unable to compare.")
            raise Exception
        if self.value == limit1 or self.value == limit2:
            return True

        if limit1 > limit2:
            if self.value > limit1 or self.value < limit2:
                return True
            else:
                return False
        elif limit1 < limit2:
            if self.value > limit1 and self.value < limit2:
                return True
            else:
                return False
        else:
            # limit1 == limit2
            raise Exception

    #def modulo(self, modulator):


class Uid(Key):
    
    # TODO  implem modulo, soustraction
    def __init__(self, ip, port):
        hash = hashlib.sha256(ip + ":" + port)
        self.idlength = 256
        self.value = hash.hexdigest()

    def sum(self, value):
        if value is int:
            return self.sumint(value)
        elif value is str:
            return self.sumhex(value)
        else:
            #self.log.error("Sum with unknow type")
            raise TypeError

    # TODO handle case when sum put key greater than FFFFF...
    def sumint(self, value):
        '''
        Return the result of the sum uid + value
        @param value: int to sum with uid value
        '''
        res = int(self.value, 16) + value
        return hex(res).split("0x")[1]
    
    def sumhex(self, value):
        return hex(int(self.value, 16) + int(value, 16)).split("0x")[1]


class Node(object):
    def __init__(self, ip, port):
        self.uid = Uid(ip, port)
        self.successor = self
        self.finger = []
        self.initfinger()

        # self.logging
        self.log = logging.getLogger(self.uid.value[:5])
        self.log.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(levelname)s - %(name)s - %(message)s')
        ch.setFormatter(formatter)
        self.log.addHandler(ch)

        self.log.debug("node creation: uid={};".format(self.uid.value))

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
        UPdate finger table for all ring
        @param newnode: new node which imply this update
        @param firstnode: node which launch the update
        '''
        for i in range(0, self.uid.idlength):
            self.finger[i] = self.lookupfinger(i, self.uid.idlength)
        if firstnode is not self.successor:
            self.successor.updatefinger(newnode, firstnode)

    def lookupfinger(self, k, m):
        '''
        Returns the node responsible for finger k
        @param m: bits number to create the ring.
            Ring is constituted of 2^m nodes maximum
        '''
        return self.lookup(self.calcfinger(k, m))

            
    def lookup(self, key):
        
        if isinstance(key, Node):
            key = node.uid
        elif isinstance(key, Key):
            key = key
        else:
            key = Key(key)
        # Self is successor ?
        if self.uid.value == key.value:
            return self
        # Is self.successor the successor of key ? 
        if key.isbetween(self.uid.value, self.successor.uid.value):
            return self.successor
        
        return self.successor.lookup(key)

    def calcfinger(self, k, m):
        '''
        Returns computed key for finger k while ring is module 2^m
        @param k: from 0 to (m - 1)
        '''
        # WIP TODO modulo to implement in Key class
        return str(self.uid.sumint(pow(2, k))) # % pow(2, m))

    def printFingers(self):
        for n, f in enumerate(self.finger):
            self.log.debug("TABLE:    finger{}: {}".format(n, f.uid.value))
            self.log.debug("COMPUTED: finger{}: {}".format(n, self.lookupfinger(n, self.uid.idlength).uid.value))
            if f.uid.value != self.lookupfinger(n, self.uid.idlength).uid.value:
                self.log.error("error")

    def printRing(self):
        succ = self.successor
        self.log.debug("Ring")
        self.log.debug(self.uid.value)
        key = self.successor.uid.value
        while key != self.uid.value:
            self.log.debug(key)
            succ = succ.successor
            key = succ.uid.value


if __name__ == "__main__":

    ip = "127.0.0.1"

    node0 = Node(ip, "0")
    node1 = Node(ip, "1")
    node2 = Node(ip, "2")
    node3 = Node(ip, "3")
    node4 = Node(ip, "4")
    node5 = Node(ip, "5")
    node6 = Node(ip, "6")
    node7 = Node(ip, "7")

    node0.addToRing(node1)
    node1.addToRing(node2)
    node1.addToRing(node3)
    node3.addToRing(node4)
    node3.addToRing(node5)
    node5.addToRing(node6)
    node1.addToRing(node7)
    
    node0.printRing()
    node1.printRing()
    node2.printRing()
    node3.printRing()
    node4.printRing()
    node5.printRing()
    node6.printRing()
    node7.printRing()

    node0.printFingers()
    node1.printFingers()
    node2.printFingers()
    node3.printFingers()
    node4.printFingers()
    node5.printFingers()
    node6.printFingers()
    node7.printFingers()
    print "succ de 03:" + node2.lookup("3").uid.value
    print "succ de 03:" + node3.lookup("3").uid.value
    print "succ de 03:" + node4.lookup("3").uid.value
    print "succ de 03:" + node5.lookup("3").uid.value
    print "succ de 03:" + node6.lookup("3").uid.value
    print "succ de 03:" + node7.lookup("3").uid.value
    print "succ de 03:" + node0.lookup("3").uid.value

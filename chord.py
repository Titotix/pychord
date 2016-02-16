import logging
import hashlib
from simplejson import dumps, loads


class Key(object):

    def __init__(self, value):
        self.value = value
        self.idlength = 256

    def __repr__(self):
        return self.value[:7]

    def canonicalize(self, value):
        '''
        Returns the str repr of hexa value with the right number of hexa char
        Basically padd the input with'0' and get rid of '0x' and 'L'
        '''
        return format(value, '0>{}x'.format(self.idlength/4))
        
    def __add__(self, value):
        if isinstance(value, int) or isinstance(value, long):
            return self.sumint(value)
        elif isinstance(value, str):
            return self.sumhex(value)
        elif isinstance(value, Key):
            return self.sumhex(value.value)
        else:
            #self.log.error("Sum with unknow type")
            print type(value)
            raise TypeError
    
    def sumint(self, value):
        '''
        Return sum uid + value in hexa representation
        @param value: int to sum with uid value
        '''
        res = (int(self.value, 16) + value) % pow(2, self.idlength)
        return self.canonicalize(res)

    def sumhex(self, value):
        res = (int(self.value, 16) + int(value, 16)) % pow(2, self.idlength)
        return self.canonicalize(res)

    def __sub__(self, value):
        if isinstance(value, int):
            return self.subint(value)
        elif isinstance(value, str):
            return self.subhex(value)
        elif isinstance(value, Key):
            return self.subhex(value.value)
        else:
            #self.log.error("Sub with unknow type")
            raise TypeError
    
    def subint(self, value):
        '''
        Return sub uid - value in hexa representation
        @param value: int to sub with uid value
        '''
        res = (int(self.value, 16) - value) % pow(2, self.idlength)
        return self.canonicalize(res)

    def subhex(self, value):
        '''
        Return sub uid - value in hexa representation
        @param value: str repr of hexa number
        '''
        res = (int(self.value, 16) - int(value, 16)) % pow(2, self.idlength)
        return self.canonicalize(res)

    
    # TODO optim : each isbetween call will be a RPC, sad if we locally know the value of remote node ?
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

class Uid(Key):
    
    def __init__(self, ip, port):
        hash = hashlib.sha256(ip + ":" + port)
        Key.__init__(self, hash.hexdigest())


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

    def __repr__(self):
        return repr(self.uid)

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
        UPdate finger table for all ring
        finger is an array of dict {resp, key}
            `resp` is the Node responsible for `key`
        @param newnode: new node which imply this update
        @param firstnode: node which launch the update
        '''
        for i in range(0, self.uid.idlength):
            fingerkey = self.calcfinger(i, self.uid.idlength)
            resp = self.lookup(fingerkey, useOnlySucc=True)
            self.finger[i] = {"resp": resp, "key": fingerkey}
            #self.finger[i] = self.lookupfinger(i, self.uid.idlength, useOnlySucc=True)
        if firstnode is not self.successor:
            self.successor.updatefinger(newnode, firstnode)

    def lookupfinger(self, k, m, useOnlySucc=False):
        '''
        Returns the node responsible for finger k
        @param m: Id length of the ring. (m = Key.idlength)
            Ring is constituted of 2^m nodes maximum
        '''
        return self.lookup(self.calcfinger(k, m), useOnlySucc)

            
    def lookup(self, key, useOnlySucc=False):
        
        if isinstance(key, Node):
            key = node.uid
        elif isinstance(key, Key):
            key = key
        elif isinstance(key, str):
            key = Key(key)
        else:
            raise Exception
        if useOnlySucc:
            # Self is successor ?
            if self.uid.value == key.value:
                return self
            # Is self.successor the successor of key ? 
            if key.isbetween(self.uid.value, self.successor.uid.value):
                return self.successor
            
            return self.successor.lookup(key, useOnlySucc)
        else:
            # Use finger table to optim lookup
            if key > self.finger[self.uid.idlength - 1]["resp"]:
                return self.finger[self.uid.idlength - 1]["resp"].lookup(key, useOnlySucc)
            else:
                # self knows the answer because key < (self finger max)

                pass
                self.log.error("no way")

    def calcfinger(self, k, m):
        '''
        Returns computed key for finger k while ring is module 2^m
        @param k: from 0 to (m - 1)
        '''
        return self.uid + pow(2, k)

    def printFingers(self):
        for n, f in enumerate(self.finger):
            self.log.debug("TABLE:    finger{0}:"
                "\n\rkey:    {2}\n\rresp:   {1}"
                .format(n, f["resp"].uid.value, f["key"]))
            if f["resp"].uid.value != self.lookupfinger(n, self.uid.idlength, useOnlySucc=True).uid.value:
                self.log.error("error between finger table and computed value")

    def printRing(self):
        succ = self.successor
        self.log.debug("Ring")
        self.log.debug(self.uid.value)
        key = self.successor.uid.value
        while key != self.uid.value:
            self.log.debug(key)
            succ = succ.successor
            key = succ.uid.value


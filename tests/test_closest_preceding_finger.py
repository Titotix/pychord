import unittest
import chord
import random
import tests.commons
import key

class TestClosestPrecedingFingerLonelyNode(unittest.TestCase):
    def setUp(self):
        #TODO create a function in commons for setup of nodes
        self.ip = "127.0.0.1"
        self.port = 2221
        self.existingnode = chord.LocalNode(self.ip, self.port)

    def tearDown(self):
        self.existingnode.stopXmlRPCServer()

    def test_with_lonely_node(self):
        self.assertEqual(
                self.existingnode.closest_preceding_finger("a"*64)["uid"],
                self.existingnode.uid
        )
        self.assertEqual(
                self.existingnode.closest_preceding_finger("1"*64)["uid"],
                self.existingnode.uid
        )
        keytolookfor = self.existingnode.uid - 1
        self.assertEqual(
                self.existingnode.closest_preceding_finger(keytolookfor)["uid"],
                self.existingnode.uid
        )

class TestClosestPrecedingFingerTwoNode(unittest.TestCase):
    def setUp(self):
        self.ip = "127.0.0.1"
        existingnode_port = random.randint(1025, 65336)
        joiningnode_port = random.randint(1025, 65335)
        if joiningnode_port == existingnode_port:
            joiningnode_port += 1
        self.existingnode = chord.LocalNode(self.ip, existingnode_port)
        self.joiningnode = chord.LocalNode(self.ip, joiningnode_port)
        self.rexistingnode = chord.RemoteNode(self.ip, existingnode_port)
        self.rjoiningnode = chord.RemoteNode(self.ip, joiningnode_port)

    def tearDown(self):
        self.existingnode.stopXmlRPCServer()
        self.joiningnode.stopXmlRPCServer()

    def test_with_two_node(self):
        for i in range(0, self.existingnode.uid.idlength):
            if self.existingnode.fingers[i].key.isbetween(self.existingnode.uid, self.joiningnode.uid):
                self.existingnode.fingers[i].setnode(self.rjoiningnode)
            else:
                self.existingnode.fingers[i].setnode(self.rexistingnode)
        for i in range(0, self.joiningnode.uid.idlength):
            if self.joiningnode.fingers[i].key.isbetween(self.joiningnode.uid, self.existingnode.uid):
                self.joiningnode.fingers[i].setnode(self.rexistingnode)
            else:
                self.joiningnode.fingers[i].setnode(self.rjoiningnode)

        keytolookfor = self.existingnode.uid - 1
        self.assertEqual(
                self.existingnode.closest_preceding_finger(keytolookfor)["uid"],
                self.joiningnode.uid.value
        )

class TestClosestPrecedingFingerThreeNode(unittest.TestCase):
    def setUp(self):
        self.ip = "127.0.0.1"
        existingnode_port = random.randint(1025, 65336)
        joiningnode_port = random.randint(1025, 65335)
        thirdnode_port = random.randint(1025, 65334)
        if joiningnode_port == existingnode_port:
            joiningnode_port += 1
        if thirdnode_port == existingnode_port\
                or thirdnode_port == joiningnode_port:
            joiningnode_port += 2
        # existingnode_port,joiningnode_port,thirdnode_port = (13525, 51633, 30381)
        self.existingnode = chord.LocalNode(self.ip, existingnode_port)
        self.joiningnode = chord.LocalNode(self.ip, joiningnode_port)
        self.thirdnode = chord.LocalNode(self.ip, thirdnode_port)
        print("Tested node port: (%i, %i, %i)" % (existingnode_port, joiningnode_port, thirdnode_port))

    def tearDown(self):
        self.existingnode.stopXmlRPCServer()
        self.joiningnode.stopXmlRPCServer()
        self.thirdnode.stopXmlRPCServer()

    def test_closest_preceding_finger_three_node(self):
        tests.commons.hardsetfingers(
                self.existingnode,
                self.joiningnode,
                self.thirdnode
        )

        keytolookfor = self.existingnode.uid - 1
        answer = None
        distanceanswer = key.Key("f"*64)
        for node in [self.existingnode, self.joiningnode, self.thirdnode]:
            # by iterate over all fingers
            # we look for the closest preceding finger for keytolookfor
            for i in range(0, node.uid.idlength):
                if node.fingers[i].node.uid.isbetween(node.uid, keytolookfor):
                    distance = key.Key(keytolookfor) - node.fingers[i].node.uid.value
                    if key.Key(distance) < distanceanswer:
                        answer = node.fingers[i].node.uid.value
                        distanceanswer = key.Key(distance)
            if not answer:
                answer = node.uid.value
            # comapring answer to closest_preceding_finger() result
            self.assertEqual(
                    answer,
                    node.closest_preceding_finger(keytolookfor)["uid"]
            )
            distanceanswer = key.Key("f"*64)
            answer = None

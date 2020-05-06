import unittest
import chord
import random
import tests.commons

class TestFindSuccessorLonelyNode(unittest.TestCase):
    def setUp(self):
        self.ip = "127.0.0.1"
        self.port = 2221
        self.existingnode = chord.LocalNode(self.ip, self.port)

    def tearDown(self):
        self.existingnode.stopXmlRPCServer()

    def test_with_lonely_node(self):
        self.assertEqual(
                self.existingnode.find_successor("a"*64)["uid"],
                self.existingnode.uid
        )
        self.assertEqual(
                self.existingnode.find_successor("1"*64)["uid"],
                self.existingnode.uid
        )
        keytolookfor = self.existingnode.uid - 1
        self.assertEqual(
                self.existingnode.find_successor(keytolookfor)["uid"],
                self.existingnode.uid
        )

class TestFindSuccessorTwoNode(unittest.TestCase):
    """
    Test find_successor methods on a two node ring
    Fingers of the ring are set "manually" not with chord algorithm
    """
    def setUp(self):
        self.ip = "127.0.0.1"
        existingnode_port = random.randint(1025, 65336)
        joiningnode_port = random.randint(1025, 65335)
        if joiningnode_port == existingnode_port:
            joiningnode_port += 1
        self.existingnode = chord.LocalNode(self.ip, existingnode_port)
        self.joiningnode = chord.LocalNode(self.ip, joiningnode_port)

    def tearDown(self):
        self.existingnode.stopXmlRPCServer()
        self.joiningnode.stopXmlRPCServer()

    def test_with_two_node(self):
        tests.commons.hardsetfingers(
                self.existingnode,
                self.joiningnode
        )

        keytolookfor = self.existingnode.uid - 1
        self.assertEqual(
                self.existingnode.find_successor(keytolookfor)["uid"],
                self.existingnode.uid.value
        )
        keytolookfor = self.existingnode.uid + 1
        self.assertEqual(
                self.existingnode.find_successor(keytolookfor)["uid"],
                self.joiningnode.uid.value
        )

class TestFindSuccessorThreeNode(unittest.TestCase):
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
        self.existingnode = chord.LocalNode(self.ip, existingnode_port)
        self.joiningnode = chord.LocalNode(self.ip, joiningnode_port)
        self.thirdnode = chord.LocalNode(self.ip, thirdnode_port)
        print("Tested node port: %i - %i - %i" % (existingnode_port, joiningnode_port, thirdnode_port))

    def tearDown(self):
        self.existingnode.stopXmlRPCServer()
        self.joiningnode.stopXmlRPCServer()
        self.thirdnode.stopXmlRPCServer()

    def test_with_three_node(self):
        tests.commons.hardsetfingers(
                self.existingnode,
                self.joiningnode,
                self.thirdnode
        )

        keytolookfor = self.existingnode.uid - 1
        for node in [self.existingnode, self.joiningnode, self.thirdnode]:
            self.assertEqual(
                    node.find_successor(keytolookfor)["uid"],
                    self.existingnode.uid.value
            )

        keytolookfor = self.existingnode.uid + 1
        if self.existingnode.uid.isbetween(self.joiningnode.uid, self.thirdnode.uid):
            answer = self.thirdnode.uid.value
        else:
            answer = self.joiningnode.uid.value
        for node in [self.existingnode, self.joiningnode, self.thirdnode]:
            self.assertEqual(
                    node.find_successor(keytolookfor)["uid"],
                    answer
            )

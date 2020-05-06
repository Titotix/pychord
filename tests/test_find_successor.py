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
        self.nodes = tests.commons.createlocalnodes(
                2,
                setfingers=True,
                setpredecessor=True
        )

    def tearDown(self):
        tests.commons.stoplocalnodes(self.nodes)

    def test_with_two_node(self):

        keytolookfor = self.nodes[0].uid - 1
        self.assertEqual(
                self.nodes[0].find_successor(keytolookfor)["uid"],
                self.nodes[0].uid.value
        )
        keytolookfor = self.nodes[0].uid + 1
        self.assertEqual(
                self.nodes[0].find_successor(keytolookfor)["uid"],
                self.nodes[1].uid.value
        )
        #TODO add test from nodes[1]

class TestFindSuccessorThreeNode(unittest.TestCase):
    def setUp(self):
        self.nodes = tests.commons.createlocalnodes(
                3,
                setfingers=True,
                setpredecessor=True
        )

    def tearDown(self):
        tests.commons.stoplocalnodes(self.nodes)

    def test_with_three_node(self):
        keytolookfor = self.nodes[0].uid - 1
        for node in self.nodes:
            self.assertEqual(
                    node.find_successor(keytolookfor)["uid"],
                    self.nodes[0].uid.value
            )

        keytolookfor = self.nodes[0].uid + 1
        if self.nodes[0].uid.isbetween(self.nodes[1].uid, self.nodes[2].uid):
            answer = self.nodes[2].uid.value
        else:
            answer = self.nodes[1].uid.value
        for node in [self.nodes[0], self.nodes[1], self.nodes[2]]:
            self.assertEqual(
                    node.find_successor(keytolookfor)["uid"],
                    answer
            )

import unittest
import chord
import random
import tests.commons
import key

class TestClosestPrecedingFingerLonelyNode(unittest.TestCase):
    def setUp(self):
        self.node = tests.commons.createlocalnodes(1)[0]

    def tearDown(self):
        tests.commons.stoplocalnodes([self.node])

    def test_with_lonely_node(self):
        self.assertEqual(
                self.node.closest_preceding_finger("a"*64)["uid"],
                self.node.uid
        )
        self.assertEqual(
                self.node.closest_preceding_finger("1"*64)["uid"],
                self.node.uid
        )
        keytolookfor = self.node.uid - 1
        self.assertEqual(
                self.node.closest_preceding_finger(keytolookfor)["uid"],
                self.node.uid
        )

class TestClosestPrecedingFingerTwoNode(unittest.TestCase):
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
                self.nodes[0].closest_preceding_finger(keytolookfor)["uid"],
                self.nodes[1].uid.value
        )

class TestClosestPrecedingFingerThreeNode(unittest.TestCase):
    def setUp(self):
        self.nodes = tests.commons.createlocalnodes(
                3,
                setfingers=True,
                setpredecessor=True
        )

    def tearDown(self):
        tests.commons.stoplocalnodes(self.nodes)

    def test_closest_preceding_finger_three_node(self):
        #TODO test for more keytolookfor
        keytolookfor = self.nodes[0].uid - 1
        answer = None
        distanceanswer = key.Key("f"*64)
        for node in self.nodes:
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

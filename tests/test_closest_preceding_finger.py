import unittest
import chord
import random
import tests.commons
import key

class TestCaseClosestPrecedingFinger(unittest.TestCase):
    def assertClosestPrecedingFinger(self, nodes, keytolookfor):
        for node in nodes:
            answer = None
            if node.uid == keytolookfor:
                answer = node.predecessor.uid.value
            if not answer:
                # by iterate over all fingers
                # we look for the closest preceding finger for keytolookfor
                distanceanswer = key.Key("f"*64) #max distance
                for i in range(0, node.uid.idlength):
                    if node.fingers[i].respNode.uid.is_between_l_inclu(node.uid, keytolookfor):
                        distance = key.Key(keytolookfor) - node.fingers[i].respNode.uid.value
                        if key.Key(distance) < distanceanswer:
                            answer = node.fingers[i].respNode.uid.value
                            distanceanswer = key.Key(distance)
                if not answer:
                    answer = node.uid.value
            # comparing answer to closest_preceding_finger() result
            try:
                res = node.closest_preceding_finger(keytolookfor)["uid"]
                self.assertEqual(
                        answer,
                        res
                )
            except AssertionError as e:
                breakpoint()
                mess = e.args[0]
                e.args = (mess + "\n"
                        "Value asked to closest_preceding_finger:   '%s'\n"
                        "closest_preceding_finger called from node: '%s'\n"
                        "Expected answered value:                   '%s'\n"
                        "closest_preceding_finger result value:     '%s'\n"
                        "All nodes uid:\n"
                        "* '{}'".format("'\n* '".join([x.uid.value for x in self.nodes]))

                        %(keytolookfor, node.uid.value, answer, res),
                )
                raise
            finally:
                distanceanswer = key.Key("f"*64)
                answer = None

class TestClosestPrecedingFingerLonelyNode(TestCaseClosestPrecedingFinger):
    def setUp(self):
        self.node = tests.commons.createlocalnodes(1, stabilizer=False)[0]

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

class TestClosestPrecedingFingerTwoNode(TestCaseClosestPrecedingFinger):
    def setUp(self):
        self.nodes = tests.commons.createlocalnodes(
                2,
                setfingers=True,
                setpredecessor=True,
                stabilizer=False
        )

    def tearDown(self):
        tests.commons.stoplocalnodes(self.nodes)

    def test_with_two_node(self):
        keytolookfor = self.nodes[0].uid - 1
        self.assertEqual(
                self.nodes[0].closest_preceding_finger(keytolookfor)["uid"],
                self.nodes[1].uid.value
        )

        keytolookfor = "0" * 64
        self.assertClosestPrecedingFinger(self.nodes, keytolookfor)

class TestClosestPrecedingFingerThreeNode(TestCaseClosestPrecedingFinger):
    @classmethod
    def setUpClass(self):
        self.nodes = tests.commons.createlocalnodes(
                3,
                setfingers=True,
                setpredecessor=True,
                stabilizer=False
        )

    @classmethod
    def tearDownClass(self):
        tests.commons.stoplocalnodes(self.nodes)

    def test_closest_preceding_finger_three_node(self):
        keytolookfor = self.nodes[0].uid - 1
        self.assertClosestPrecedingFinger(self.nodes, keytolookfor)

        keytolookfor = self.nodes[0].uid + 1
        self.assertClosestPrecedingFinger(self.nodes, keytolookfor)

        keytolookfor = self.nodes[1].uid + 1
        self.assertClosestPrecedingFinger(self.nodes, keytolookfor)

        keytolookfor = "0" * 64
        self.assertClosestPrecedingFinger(self.nodes, keytolookfor)

    def test_closest_preceding_finger_node_equal_key(self):
        """Test closest_preceding_finger() from all 3 nodes of the ring
        The key provided to closest_preceding_finger() are equals to
        nodes uid
        """
        for node in self.nodes:
            keytolookfor = node.uid.value
            self.assertClosestPrecedingFinger(self.nodes, keytolookfor)

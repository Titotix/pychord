import unittest
import chord
import random
import tests.commons


class TestFindSuccessorLonelyNode(unittest.TestCase):
    def setUp(self):
        self.ip = "127.0.0.1"
        self.port = 2221
        self.existingnode = chord.LocalNode(self.ip, self.port, _stabilizer=False)

    def tearDown(self):
        tests.commons.stoplocalnodes([self.existingnode])

    def test_find_successor(self):
        """
        Test find_successor from a node not connected to a ring
        All result from find_successor are exepcted to be the node itself
        """
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
                setpredecessor=True,
                stabilizer=False
        )

    def tearDown(self):
        tests.commons.stoplocalnodes(self.nodes)

    def test_find_successor(self):
        """
        Test find_successor() on a 2 nodes ring
        """

        keytolookfor = self.nodes[0].uid
        for node in self.nodes:
            self.assertEqual(
                    node.find_successor(keytolookfor)["uid"],
                    self.nodes[0].uid.value
            )
        keytolookfor = self.nodes[1].uid
        for node in self.nodes:
            self.assertEqual(
                    node.find_successor(keytolookfor)["uid"],
                    self.nodes[1].uid.value
            )
        keytolookfor = self.nodes[0].uid - 1
        self.assertEqual(
                self.nodes[0].find_successor(keytolookfor)["uid"],
                self.nodes[0].uid.value
        )
        self.assertEqual(
                self.nodes[1].find_successor(keytolookfor)["uid"],
                self.nodes[0].uid.value
        )

        keytolookfor = self.nodes[0].uid + 1
        self.assertEqual(
                self.nodes[0].find_successor(keytolookfor)["uid"],
                self.nodes[1].uid.value
        )
        self.assertEqual(
                self.nodes[1].find_successor(keytolookfor)["uid"],
                self.nodes[1].uid.value
        )

        keytolookfor = self.nodes[1].uid - 1
        self.assertEqual(
                self.nodes[0].find_successor(keytolookfor)["uid"],
                self.nodes[1].uid.value
        )
        self.assertEqual(
                self.nodes[1].find_successor(keytolookfor)["uid"],
                self.nodes[1].uid.value
        )

        keytolookfor = self.nodes[1].uid + 1
        self.assertEqual(
                self.nodes[0].find_successor(keytolookfor)["uid"],
                self.nodes[0].uid.value
        )
        self.assertEqual(
                self.nodes[1].find_successor(keytolookfor)["uid"],
                self.nodes[0].uid.value
        )

class TestFindSuccessorThreeNode(unittest.TestCase):
    """
    Test find_successor methods.
    Generates and sets statically all nodes and their fingers/predecessor.
    Doesn't use stabilizer
    """
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

    def test_find_successor_key_equal_node(self):
        """
        Test find_successor(key) on a 3 nodes ring
        Provided key is equal to nodes uid
        """
        # Test successor of a node.uid
        # answer should be the node it self
        for node_in_test in self.nodes:
            keytolookfor = node_in_test.uid.value
            for node in self.nodes:
                try:
                    res = node.find_successor(keytolookfor)["uid"]
                    self.assertEqual(
                            res,
                            node_in_test.uid.value
                    )
                except AssertionError as e:
                    mess = e.args[0]
                    e.args = (mess + "\n"
                            "Value asked to find_successor:   '%s'\n"
                            "find_successor called from node: '%s'\n"
                            "Expected answered value:         '%s'\n"
                            "find_successor result value:     '%s'\n"
                            "All nodes uid:\n"
                            "* '{}'".format("'\n* '".join([x.uid.value for x in self.nodes]))

                            %(keytolookfor, node.uid.value, node_in_test.uid.value, res),
                    )
                    raise

    def test_find_successor_uid_minus_one(self):
        """Test successor of node.uid - 1
         result should be this node
        """
        #TODO implement same loop than test_find_successor_node_plus_one()
        # with exception handling (more output if error)
        keytolookfor = self.nodes[0].uid - 1
        for node in self.nodes:
            self.assertEqual(
                    node.find_successor(keytolookfor)["uid"],
                    self.nodes[0].uid.value
            )

        keytolookfor = self.nodes[1].uid - 1
        for node in self.nodes:
            self.assertEqual(
                    node.find_successor(keytolookfor)["uid"],
                    self.nodes[1].uid.value
            )

        keytolookfor = self.nodes[2].uid - 1
        for node in self.nodes:
            self.assertEqual(
                    node.find_successor(keytolookfor)["uid"],
                    self.nodes[2].uid.value
            )

    def test_find_successor_uid_plus_one(self):
        """
        Test find_successor on node.uid + 1 for a 3 nodes ring
        """
        # FOr all nodes we search "manually" the successor of it's uid+1
        # Then for all nodes,
        # assert that find_successor's answer is what we manually look for
        for i, node in enumerate(self.nodes):
            node1 = self.nodes[(i+1) % len(self.nodes)]
            node2 = self.nodes[(i+2) % len(self.nodes)]
            keytolookfor = node.uid + 1
            if node.uid.isbetween(node1.uid, node2.uid):
                answer = node2.uid.value
            else:
                answer = node1.uid.value
            for nodeToAsk in self.nodes:
                try:
                    res = nodeToAsk.find_successor(keytolookfor)["uid"]
                    self.assertEqual(
                            res,
                            answer
                    )
                except AssertionError as e:
                    mess = e.args[0]
                    e.args = (mess + "\n"
                            "Value asked to find_predecessor:   '%s'\n"
                            "find_predecessor called from node: '%s'\n"
                            "Expected answered value:           '%s'\n"
                            "find_predecessor result value:     '%s'\n"
                            "All nodes uid:\n"
                            "* '%s'\n"
                            "* '%s'\n"
                            "* '%s'"
                            %(keytolookfor, nodeToAsk.uid.value, answer, res,
                            node1.uid.value, node2.uid.value, node.uid.value),
                    )
                    raise

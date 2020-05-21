import unittest
import chord
import random
import tests.commons

class TestFindpredecessorTwoNode(unittest.TestCase):
    """
    Test find_predecessor methods on a two node ring
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

    def test_find_predecessor(self):
        """
        Test find_predecessor() on a 2 node ring
        """

        keytolookfor = self.nodes[0].uid.value
        for node in self.nodes:
            self.assertEqual(
                    node.find_predecessor(keytolookfor)["uid"],
                    self.nodes[1].uid.value
            )

        keytolookfor = self.nodes[0].uid - 1
        for node in self.nodes:
            self.assertEqual(
                    node.find_predecessor(keytolookfor)["uid"],
                    self.nodes[1].uid.value
            )

        keytolookfor = self.nodes[0].uid + 1
        for node in self.nodes:
            self.assertEqual(
                    node.find_predecessor(keytolookfor)["uid"],
                    self.nodes[0].uid.value
            )

        keytolookfor = self.nodes[1].uid - 1
        for node in self.nodes:
            self.assertEqual(
                    node.find_predecessor(keytolookfor)["uid"],
                    self.nodes[0].uid.value
            )

        keytolookfor = self.nodes[1].uid + 1
        for node in self.nodes:
            self.assertEqual(
                    node.find_predecessor(keytolookfor)["uid"],
                    self.nodes[1].uid.value
            )

class TestFindpredecessorThreeNode(unittest.TestCase):
    """
    Test find_predecessor methods.
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

    def test_find_predecessor(self):
        """
        Test find_predecessor() on a 3 nodes ring
        """
        # For all nodes we search the predecessor of it's uid.value
        # by comparing nodes emplacement on the ring with is_between_* methods
        # Result of this search is `answer`
        # Then for all nodes,
        # assert find_predecessor()'s result is the one we previously look for
        for i, node in enumerate(self.nodes):
            node1 = self.nodes[(i+1) % len(self.nodes)]
            node2 = self.nodes[(i+2) % len(self.nodes)]
            keytolookfor = node.uid - 1
            if node.uid.is_between_exclu(node1.uid, node2.uid):
                if node1.uid != node.uid - 1:
                    answer = node1.uid.value
                else:
                    answer = node2.uid.value
            else:
                if node2.uid != node.uid - 1:
                    answer = node2.uid.value
                else:
                    answer = node1.uid.value
            for nodeToAsk in self.nodes:
                self.assertEqual(
                        nodeToAsk.find_predecessor(keytolookfor)["uid"],
                        answer
                )
        # Test predecessor of node.uid + 1 
        # answer should be this node
        for node_in_test in self.nodes:
            keytolookfor = node_in_test.uid + 1
            for node in self.nodes:
                self.assertEqual(
                        node.find_predecessor(keytolookfor)["uid"],
                        node_in_test.uid.value
                )

    def test_find_predecessor_equal_values(self):
        """
        Test find_predecessor on a 3 nodes ring with values equal to nodes uid
        """
        # For all nodes we search the predecessor of it's uid.value
        # by comparing nodes emplacement on the ring with is_between_* methods
        # Result of this search is `answer`
        # Then for all nodes,
        # assert find_predecessor()'s result is the one we previously look for
        for i, node in enumerate(self.nodes):
            node1 = self.nodes[(i+1) % len(self.nodes)]
            node2 = self.nodes[(i+2) % len(self.nodes)]
            keytolookfor = node.uid.value
            if node.uid.is_between_exclu(node1.uid, node2.uid):
                answer = node1.uid.value
            else:
                answer = node2.uid.value
            for nodeToAsk in self.nodes:
                try:
                    res = nodeToAsk.find_predecessor(keytolookfor)["uid"]
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

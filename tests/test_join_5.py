import unittest
import time
import chord
import tests.commons

class TestManualStabilize2Nodes(unittest.TestCase):
    """
    Test stabilize() inpact on successor/predecessor of node when stabilize
    is not executed periodically
    2 nodes ring
    """
    def setUp(self):
        self.nodes = tests.commons.createlocalnodes(2, stabilizer=False)
        self.nodes[1].join_5(chord.NodeInterface(self.nodes[0].asdict()))

    def tearDown(self):
        tests.commons.stoplocalnodes(self.nodes)

    def test_joining_node_successor(self):
        """
        Test if node N which join M has properly put his successor to M
        """
        self.assertEqual(
            self.nodes[1].successor.uid.value, self.nodes[0].uid.value
        )

    def test_stabilize(self):
        """
        Execute stabilize() 3 times and assert succ & prede are set correctly
        after each execution, accordingly to what this execution should have
        changed.

        Test stabilize() while it's not executed periodically
        """

        self.nodes[1].stabilize()
        self.assertEqual(self.nodes[0].predecessor.uid.value, self.nodes[1].uid.value)
        self.assertEqual(self.nodes[1].successor.uid.value, self.nodes[0].uid.value)

        self.nodes[0].stabilize()
        self.assertEqual(self.nodes[1].predecessor.uid.value, self.nodes[0].uid.value)
        self.assertEqual(self.nodes[0].successor.uid.value, self.nodes[1].uid.value)

        self.nodes[1].stabilize()
        self.assertEqual(self.nodes[0].predecessor.uid.value, self.nodes[1].uid.value)
        self.assertEqual(self.nodes[1].predecessor.uid.value, self.nodes[0].uid.value)
        self.assertEqual(self.nodes[1].successor.uid.value, self.nodes[0].uid.value)
        self.assertEqual(self.nodes[0].successor.uid.value, self.nodes[1].uid.value)

class TestManualStabilize3Nodes(unittest.TestCase):
    """
    Test stabilize() inpact on successor/predecessor of node when stabilize
    is not executed periodically
    3 nodes ring
    Nodes don't join concurrently.
    Node 1 join node 0, then stabilize of each other are executed enough time to have accurate successor for both
    Then node 2 join node 0. From their test successor/predecessor info after each stabilize execution
    """
    def setUp(self):
        self.nodes = tests.commons.createlocalnodes(3, stabilizer=False)
        self.nodes[1].join_5(chord.NodeInterface(self.nodes[0].asdict()))
        self.nodes[1].stabilize()
        self.nodes[0].stabilize()
        self.nodes[1].stabilize()

        self.nodes[2].join_5(chord.NodeInterface(self.nodes[0].asdict()))

    def tearDown(self):
        tests.commons.stoplocalnodes(self.nodes)

    def get_successor(self, node_index):
        node_tested = self.nodes[node_index]
        node1 = self.nodes[(node_index + 1) % len(self.nodes)]
        node2 = self.nodes[(node_index + 2) % len(self.nodes)]
        if node_tested.uid.is_between_exclu(node1.uid, node2.uid):
            return node2
        else:
            return node1

    def assertSuccessor(self, node_tested):
        """
        assert successor of self.nodes[node_index] is right in the 3 nodes ring
        """
        for i, n in enumerate(self.nodes):
            if n.uid == node_tested.uid:
                node_index = i
        node1 = self.nodes[(node_index + 1) % len(self.nodes)]
        node2 = self.nodes[(node_index + 2) % len(self.nodes)]
        if node_tested.uid.is_between_exclu(node1.uid, node2.uid):
            self.assertEqual(node2.uid.value, node_tested.successor.uid.value)
        else:
            self.assertEqual(node1.uid.value, node_tested.successor.uid.value)

    def assertPredecessor(self, node_tested):
        """
        assert node_tested predecessor is right in the 3 nodes ring
        """
        for i, n in enumerate(self.nodes):
            if n.uid == node_tested.uid:
                node_index = i
        node1 = self.nodes[(node_index + 1) % len(self.nodes)]
        node2 = self.nodes[(node_index + 2) % len(self.nodes)]
        if node_tested.uid.is_between_exclu(node1.uid, node2.uid):
            self.assertEqual(node1.uid.value, node_tested.predecessor.uid.value)
        else:
            self.assertEqual(node2.uid.value, node_tested.predecessor.uid.value)

    def test_stabilize(self):
        """
        Test stabilize() while it's not executed periodically
        For a 3 nodes ring
        Test successors and predecessors values for all node if the ring
        """
        self.assertSuccessor(self.nodes[2])
        self.nodes[2].stabilize()
        self.assertPredecessor(self.get_successor(2))

        self.nodes[1].stabilize()
        self.assertPredecessor(self.get_successor(1))
        self.assertSuccessor(self.nodes[1])
 
        self.nodes[0].stabilize()
        self.assertPredecessor(self.get_successor(0))
        self.assertSuccessor(self.nodes[0])

        # Check again all values
        self.assertSuccessor(self.nodes[1])
        self.assertSuccessor(self.nodes[2])
        self.assertPredecessor(self.nodes[0])
        self.assertPredecessor(self.nodes[1])
        self.assertPredecessor(self.nodes[2])

class TestPeriodicalStabilize(unittest.TestCase):
    def setUp(self):
        self.nodes = tests.commons.createlocalnodes(2)
        self.nodes[1].join_5(chord.NodeInterface(self.nodes[0].asdict()))

    def tearDown(self):
        tests.commons.stoplocalnodes(self.nodes)

    def test_stabilize(self):
        """
        Test nodes successor & predecessor after stabilize execution
        on a 2 nodes ring
        """

        # Wait few time that stabilize executed enough time on each nodes
        time.sleep(4)

        self.assertEqual(
            self.nodes[0].predecessor.uid.value, self.nodes[1].uid.value
        )
        self.assertEqual(
            self.nodes[1].successor.uid.value, self.nodes[0].uid.value
        )
        self.assertEqual(
            self.nodes[1].predecessor.uid.value, self.nodes[0].uid.value
        )
        self.assertEqual(
            self.nodes[0].successor.uid.value, self.nodes[1].uid.value
        )

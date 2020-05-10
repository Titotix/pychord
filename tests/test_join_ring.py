import unittest
import chord
import tests.commons

class TestInitFingers(unittest.TestCase):
    def setUp(self):
        self.nodes = tests.commons.createlocalnodes(2)

    def tearDown(self):
        tests.commons.stoplocalnodes(self.nodes)

    def test_init_fingers(self):
        self.nodes[1].init_fingers(chord.NodeInterface(self.nodes[0].asdict()))
        self.assertEqual(self.nodes[1].successor.uid, self.nodes[0].uid)
        self.assertEqual(self.nodes[0].successor.uid, self.nodes[1].uid)
        self.assertEqual(self.nodes[0].predecessor.uid, self.nodes[1].uid)
        self.assertEqual(self.nodes[1].predecessor.uid, self.nodes[0].uid)
        for i in range(0, self.nodes[0].uid.idlength):
            if self.nodes[1].fingers[i].key.isbetween(self.nodes[1].uid, self.nodes[0].uid):
                self.assertEqual(self.nodes[1].fingers[i].respNode.uid, self.nodes[0].uid)
            else:
                self.assertEqual(self.nodes[1].fingers[i].respNode.uid, self.nodes[1].uid)

class TestJoinTwoNodeRing(unittest.TestCase):
    def setUp(self):
        self.nodes = tests.commons.createlocalnodes(2)

    def tearDown(self):
        tests.commons.stoplocalnodes(self.nodes)

    def test_join(self):
        self.nodes[1].join(chord.NodeInterface(self.nodes[0].asdict()))
        self.assertEqual(self.nodes[1].successor.uid, self.nodes[0].uid)
        self.assertEqual(self.nodes[0].successor.uid, self.nodes[1].uid)
        self.assertEqual(self.nodes[0].predecessor.uid, self.nodes[1].uid)
        self.assertEqual(self.nodes[1].predecessor.uid, self.nodes[0].uid)
        for k, node in enumerate(self.nodes):
            othernode = self.nodes[(k+1) % 2]
            for i in range(0, node.uid.idlength):
                if node.fingers[i].key.isbetween(node.uid, othernode.uid):
                    self.assertEqual(
                            node.fingers[i].respNode.uid,
                            othernode.uid
                    )
                else:
                    self.assertEqual(
                            node.fingers[i].respNode.uid,
                            node.uid
                    )

class TestJoinThreeNodeRing(unittest.TestCase):
    def setUp(self):
        self.nodes = tests.commons.createlocalnodes(3)

    def tearDown(self):
        tests.commons.stoplocalnodes(self.nodes)

    def test_join_three_node(self):
        self.nodes[1].join(chord.NodeInterface(self.nodes[0].asdict()))
        self.nodes[2].join(chord.NodeInterface(self.nodes[0].asdict()))

        for k, node in enumerate(self.nodes):
            node1 = self.nodes[(k+1) % len(self.nodes)]
            node2 = self.nodes[(k+2) % len(self.nodes)]
            if node.uid.isbetween(node1.uid, node2.uid):
                nodesuccessor = node2
                nodepredecessor = node1
            else:
                nodesuccessor = node1
                nodepredecessor = node2
            # Assert predecessor and successor
            self.assertEqual(
                    node.predecessor.uid,
                    nodepredecessor.uid
            )
            self.assertEqual(
                    node.successor.uid,
                    nodesuccessor.uid
            )
            #Loop to assert all fingers of node
            for i in range(0, node.uid.idlength):
                if node.fingers[i].key.isbetween(node.uid, nodesuccessor.uid):
                    self.assertEqual(
                            node.fingers[i].respNode.uid,
                            nodesuccessor.uid
                    )
                elif node.fingers[i].key.isbetween(nodesuccessor.uid, nodepredecessor.uid):
                    self.assertEqual(
                            node.fingers[i].respNode.uid,
                            nodepredecessor.uid
                    )
                else:
                    self.assertEqual(
                            node.fingers[i].respNode.uid,
                            node.uid
                    )

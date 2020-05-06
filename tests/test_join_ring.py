import unittest
import chord
import tests.commons

class TestInitFingers(unittest.TestCase):
    def setUp(self):
        self.ip = "127.0.0.1"
        self.port = [2221, 2222]
        self.existingnode = chord.LocalNode(self.ip, self.port[0])
        self.joiningnode = chord.LocalNode(self.ip, self.port[1])
        self.existingnoderemote = chord.RemoteNode(self.ip, self.port[0])

    def tearDown(self):
        self.existingnode.stopXmlRPCServer()
        self.joiningnode.stopXmlRPCServer()

    def test_init_fingers(self):
        self.joiningnode.init_fingers(self.existingnoderemote)
        self.assertEqual(self.joiningnode.successor.uid, self.existingnode.uid)
        self.assertEqual(self.existingnode.successor.uid, self.joiningnode.uid)
        self.assertEqual(self.existingnode.predecessor.uid, self.joiningnode.uid)
        self.assertEqual(self.joiningnode.predecessor.uid, self.existingnode.uid)
        for i in range(0, self.existingnode.uid.idlength):
            if self.joiningnode.fingers[i].key.isbetween(self.joiningnode.uid, self.existingnode.uid):
                self.assertEqual(self.joiningnode.fingers[i].node.uid, self.existingnode.uid)
            else:
                self.assertEqual(self.joiningnode.fingers[i].node.uid, self.joiningnode.uid)

class TestJoinTwoNodeRing(unittest.TestCase):
    def setUp(self):
        self.ip = "127.0.0.1"
        self.port = [2221, 2222]
        self.existingnode = chord.LocalNode(self.ip, self.port[0])
        self.joiningnode = chord.LocalNode(self.ip, self.port[1])
        self.existingnoderemote = chord.RemoteNode(self.ip, self.port[0])

    def tearDown(self):
        self.existingnode.stopXmlRPCServer()
        self.joiningnode.stopXmlRPCServer()

    def test_join(self):
        self.joiningnode.join(self.existingnoderemote)
        self.assertEqual(self.joiningnode.successor.uid, self.existingnode.uid)
        self.assertEqual(self.existingnode.successor.uid, self.joiningnode.uid)
        self.assertEqual(self.existingnode.predecessor.uid, self.joiningnode.uid)
        self.assertEqual(self.joiningnode.predecessor.uid, self.existingnode.uid)
        nodelist = [self.existingnode, self.joiningnode]
        for k, node in enumerate(nodelist):
            othernode = nodelist[(k+1) % 2]
            for i in range(0, node.uid.idlength):
                if node.fingers[i].key.isbetween(node.uid, othernode.uid):
                    self.assertEqual(
                            node.fingers[i].node.uid,
                            othernode.uid
                    )
                else:
                    self.assertEqual(
                            node.fingers[i].node.uid,
                            node.uid
                    )

class TestJoinThreeNodeRing(unittest.TestCase):
    def setUp(self):
        self.nodes = tests.commons.createlocalnodes(3)

    def tearDown(self):
        tests.commons.stoplocalnodes(self.nodes)

    def test_join_three_node(self):
        self.nodes[1].join(chord.RemoteNode(self.nodes[0].asdict()))
        self.nodes[2].join(chord.RemoteNode(self.nodes[0].asdict()))

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
                            node.fingers[i].node.uid,
                            nodesuccessor.uid
                    )
                elif node.fingers[i].key.isbetween(nodesuccessor.uid, nodepredecessor.uid):
                    self.assertEqual(
                            node.fingers[i].node.uid,
                            nodepredecessor.uid
                    )
                else:
                    self.assertEqual(
                            node.fingers[i].node.uid,
                            node.uid
                    )

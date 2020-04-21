import unittest
import chord

class NodeLookupTest(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.ip = "127.0.0.1"
        self.port = [2221, 2222, 2223]
        self.node0 = chord.Node(self.ip, self.port[0])
        self.node1 = chord.Node(self.ip, self.port[1])
        self.node2 = chord.Node(self.ip, self.port[2])
        # For ease of test writing/understanging with set custom uid
        self.node0.uid.setValue("0"*64)
        self.node1.uid.setValue("1"*64)
        self.node2.uid.setValue("2"*64)

        self.node0.addToRing(self.node1)
        self.node0.addToRing(self.node2)

    @classmethod
    def tearDownClass(self):
        self.node0.stopXmlRPCServer()
        self.node1.stopXmlRPCServer()
        self.node2.stopXmlRPCServer()

    def test_lookup_useOnlySucc(self):
        self.assertTrue(self.node0.lookup("1".zfill(64), useOnlySucc=True) is self.node1)
        self.assertTrue(self.node0.lookup("a"*64, useOnlySucc=True) is self.node0)
        self.assertTrue(self.node1.lookup("a"*64, useOnlySucc=True) is self.node0)
        self.assertTrue(self.node2.lookup("a"*64, useOnlySucc=True) is self.node0)

class NodeBasicMethodsTest(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.ip = "127.0.0.1"
        self.port = [2000, 2001, 2002]
        self.node0 = chord.Node(self.ip, self.port[0])
        
class NodeaddToRingTest(unittest.TestCase):

    def setUp(self):
        self.ip = "127.0.0.1"
        self.port = [8000, 8001, 8002, 8003, 8004]
        self.node0 = chord.Node(self.ip, self.port[0])
        self.node1 = chord.Node(self.ip, self.port[1])
        self.node2 = chord.Node(self.ip, self.port[2])
        # For ease of test writing/understanging with set custom uid
        self.node0.uid.setValue("0"*64)
        self.node1.uid.setValue("1"*64)
        self.node2.uid.setValue("2"*64)

    def tearDown(self):
        self.node0.stopXmlRPCServer()
        self.node1.stopXmlRPCServer()
        self.node2.stopXmlRPCServer()

    def test_TwoNodesRing(self):
        """
        Test addToRing methods with a ring of 2 nodes only
        Check if successor attr is the proper one
        """
        self.assertFalse(self.node0.successor is self.node1)
        self.assertFalse(self.node1.successor is self.node0)
        self.node0.addToRing(self.node1)
        self.assertTrue(self.node0.successor is self.node1)
        self.assertTrue(self.node1.successor is self.node0)

    def test_ThreeNodesRing_mainNode(self):
        """
        Test addToRing methods with a ring of 3 nodes only
        Two nodes are added from a 'main one'
        Check if successor attr is the proper one
        """
        self.node0.addToRing(self.node1)
        self.node0.addToRing(self.node2)
        self.assertTrue(self.node0.successor is self.node1)
        self.assertTrue(self.node1.successor is self.node2)
        self.assertTrue(self.node2.successor is self.node0)

    def test_ThreeNodesRing(self):
        """
        Test addToRing methods with a ring of 3 nodes
        node1 added by node0, node 2 added by node1 (aka no 'main node')
        Check if successor attr is the proper one
        """
        self.node0.addToRing(self.node1)
        self.node1.addToRing(self.node2)
        self.assertTrue(self.node0.successor is self.node1)
        self.assertTrue(self.node1.successor is self.node2)
        self.assertTrue(self.node2.successor is self.node0)

import unittest
import chord

class NodeLookupTest(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.ip = "127.0.0.1"
        self.port = [2221, 2222, 2223]
        self.node0 = chord.LocalNode(self.ip, self.port[0])
        self.node1 = chord.LocalNode(self.ip, self.port[1])
        self.node2 = chord.LocalNode(self.ip, self.port[2])

        self.node0.addToRing(chord.BasicNode(self.node1.ip, self.node1.port))
        self.node0.addToRing(chord.BasicNode(self.node2.ip, self.node2.port))

    @classmethod
    def tearDownClass(self):
        self.node0.stopXmlRPCServer()
        self.node1.stopXmlRPCServer()
        self.node2.stopXmlRPCServer()

    def test_lookupWithSucc(self):
        #node0 a2fa69d06e3fdca9e022f993e81081d3cc65b262d4a77bd47caa190b7180d354
        #node1 4e03fd4d8bfdf5b10d1d6bbda1bc91caffb6be6740e3baade0851c3b57b3a140
        #node2 e40ba7ecf4e34deb177ed2bcca881338e8b98502e3f3ebab4a122b75bd6ba18f
        keyTolookup = self.node0.uid + 1
        res = self.node0.lookupWithSucc(keyTolookup)
        noderes = chord.BasicNode(res["ip"], res["port"])
        self.assertEqual(noderes.uid.value, self.node2.uid.value)

        keyTolookup = self.node1.uid + 1
        res = self.node0.lookupWithSucc(keyTolookup)
        noderes = chord.BasicNode(res["ip"], res["port"])
        self.assertEqual(noderes.uid.value, self.node0.uid.value)

        keyTolookup = self.node2.uid + 1
        res = self.node0.lookupWithSucc(keyTolookup)
        noderes = chord.BasicNode(res["ip"], res["port"])
        self.assertEqual(noderes.uid.value, self.node1.uid.value)

class NodeaddToRingTest(unittest.TestCase):

    def setUp(self):
        self.ip = "127.0.0.1"
        self.port = [2221, 2222, 2223]
        #node0 a2fa69d06e3fdca9e022f993e81081d3cc65b262d4a77bd47caa190b7180d354
        #node1 4e03fd4d8bfdf5b10d1d6bbda1bc91caffb6be6740e3baade0851c3b57b3a140
        #node2 e40ba7ecf4e34deb177ed2bcca881338e8b98502e3f3ebab4a122b75bd6ba18f
        self.node0 = chord.LocalNode(self.ip, self.port[0])
        self.node1 = chord.LocalNode(self.ip, self.port[1])
        self.node2 = chord.LocalNode(self.ip, self.port[2])

    def tearDown(self):
        self.node0.stopXmlRPCServer()
        self.node1.stopXmlRPCServer()
        self.node2.stopXmlRPCServer()

    def test_TwoNodesRing(self):
        """
        Test addToRing methods with a ring of 2 nodes only
        Check if successor attr is the proper one
        """
        self.assertTrue(self.node0.successor is None)
        # add node1 from node0
        self.node0.addToRing(chord.BasicNode(self.node1.ip, self.node1.port))
        # successor(node0) == node1 ?
        self.assertEqual(self.node0.successor.uid.value, self.node1.uid.value)
        # successor(node1) == node0 ?
        self.assertEqual(self.node1.successor.uid.value, self.node0.uid.value)

    def test_ThreeNodesRing_mainNode(self):
        """
        Test addToRing methods with a ring of 3 nodes only
        Two nodes are added from the same node
        it provides a BasicNode to addToRing method
        Check if successor attr is the proper one
        """
        # add node1 from node0
        self.node0.addToRing(chord.BasicNode(self.node1.ip, self.node1.port))
        # add node2 from node0
        self.node0.addToRing(chord.BasicNode(self.node2.ip, self.node2.port))

        self.assertEqual(self.node0.successor.uid.value, self.node2.uid.value)
        self.assertEqual(self.node1.successor.uid.value, self.node0.uid.value)
        self.assertEqual(self.node2.successor.uid.value, self.node1.uid.value)

        #node0 a2fa69d06e3fdca9e022f993e81081d3cc65b262d4a77bd47caa190b7180d354
        #node1 4e03fd4d8bfdf5b10d1d6bbda1bc91caffb6be6740e3baade0851c3b57b3a140
        #node2 e40ba7ecf4e34deb177ed2bcca881338e8b98502e3f3ebab4a122b75bd6ba18f
#    def test_ThreeNodesRing(self):
#        """
#        Test addToRing methods with a ring of 3 nodes
#        node1 added by node0, node 2 added by node1 (aka no 'main node')
#        Check if successor attr is the proper one
#        """
#        self.node0.addToRing(self.node1)
#        self.node1.addToRing(self.node2)
#        self.assertTrue(self.node0.successor is self.node1)
#        self.assertTrue(self.node1.successor is self.node2)
#        self.assertTrue(self.node2.successor is self.node0)

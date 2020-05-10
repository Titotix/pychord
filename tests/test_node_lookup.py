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

        self.node1.join(chord.NodeInterface({"ip":self.node0.ip, "port":self.node0.port}))
        self.node2.join(chord.NodeInterface({"ip": self.node0.ip, "port": self.node0.port}))

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

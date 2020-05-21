import unittest
import chord
import tests.commons

class NodeLookupTest(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.ip = "127.0.0.1"
        self.port = [2221, 2222, 2223]
        self.nodes = tests.commons.createlocalnodes(
            3, 2221, 2222, 2223,
            setfingers=True, setpredecessor=True, stabilizer=False
        )

    @classmethod
    def tearDownClass(self):
        tests.commons.stoplocalnodes(self.nodes)

    def test_lookupWithSucc(self):
        #nodes[0] a2fa69d06e3fdca9e022f993e81081d3cc65b262d4a77bd47caa190b7180d354
        #nodes[1] 4e03fd4d8bfdf5b10d1d6bbda1bc91caffb6be6740e3baade0851c3b57b3a140
        #nodes[2] e40ba7ecf4e34deb177ed2bcca881338e8b98502e3f3ebab4a122b75bd6ba18f
        keyTolookup = self.nodes[0].uid + 1
        res = self.nodes[0].lookupWithSucc(keyTolookup)
        noderes = chord.BasicNode(res["ip"], res["port"])
        self.assertEqual(noderes.uid.value, self.nodes[2].uid.value)

        keyTolookup = self.nodes[1].uid + 1
        res = self.nodes[0].lookupWithSucc(keyTolookup)
        noderes = chord.BasicNode(res["ip"], res["port"])
        self.assertEqual(noderes.uid.value, self.nodes[0].uid.value)

        keyTolookup = self.nodes[2].uid + 1
        res = self.nodes[0].lookupWithSucc(keyTolookup)
        noderes = chord.BasicNode(res["ip"], res["port"])
        self.assertEqual(noderes.uid.value, self.nodes[1].uid.value)

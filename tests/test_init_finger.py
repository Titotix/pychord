import unittest
import chord
import tests.commons

class TestInitFingers(unittest.TestCase):
    def setUp(self):
        self.nodes = tests.commons.createlocalnodes(2, stabilizer=False)

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

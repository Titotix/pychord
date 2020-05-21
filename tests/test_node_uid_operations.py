import unittest
import chord
import hashlib

def getSha256Str(strtohash):
    hashlib.sha256(strtohash).encode("utf-8").hexdigest()

class NodeUidTest(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.ip = "127.0.0.1"
        self.port = 6000
        self.node = chord.LocalNode(self.ip, self.port, _stabilizer=False)

    @classmethod
    def tearDownClass(self):
        self.node.stopXmlRPCServer()

    def test_uid_value(self):
        self.assertEqual(self.node.uid.value,\
                hashlib.sha256("{ip}:{port}".format(\
                ip=self.ip,\
                port=self.port).encode("utf-8")).hexdigest()
        )

    def test_uid_value_length(self):
        self.assertEqual(len(self.node.uid.value), 64)

    def test_uid_type(self):
        self.assertIsInstance(self.node.uid, chord.Uid)

class KeyTest(unittest.TestCase):
    """
    Test overwritten builtin comparison for chord.Key type
    Function name format : test_<function_tested>_<type_of_arg>
    """
    @classmethod
    def setUpClass(self):
        self.ip = "127.0.0.1"
        self.port = 2000
        # while instantiate a BasicNode we get a chord.Uid() (node.uid)
        # which is a subclass of chord.Key
        # we gonna use self.node.uid to test Key features
        self.node = chord.BasicNode(self.ip, self.port)

    def test_lt_str(self):
        #compare to value
        self.assertFalse(
                self.node.uid < "f9b8b725655d34a49328e659985bc43995caeec537f01f6129ce759ccd143119")
        # compared to value +1
        self.assertTrue(
                self.node.uid < "f9b8b725655d34a49328e659985bc43995caeec537f01f6129ce759ccd14311a")

    def test_lt_int(self):
        """
        Test __lt__() with int arg
        """
        self.assertTrue(self.node.uid < (int(self.node.uid.value, 16) + 1))

    def test_le_str(self):
        """
        Test __le__() with str arg
        """
        # compare to value itself
        self.assertTrue(self.node.uid <= "f9b8b725655d34a49328e659985bc43995caeec537f01f6129ce759ccd143119")
        # compared to value +1
        self.assertTrue(self.node.uid <= "f9b8b725655d34a49328e659985bc43995caeec537f01f6129ce759ccd14311a")

    def test_le_int(self):
        """
        Test __le__() with int arg
        """
        self.assertTrue(self.node.uid <= (int(self.node.uid.value, 16) + 1))
        self.assertTrue(self.node.uid <= int(self.node.uid.value, 16))
        self.assertFalse(self.node.uid <= (int(self.node.uid.value, 16) - 1))

    def test_eq_str(self):
        """
        Test __eq__() with a str arg
        """
        self.assertTrue(self.node.uid == "f9b8b725655d34a49328e659985bc43995caeec537f01f6129ce759ccd143119")

    def test_eq_int(self):
        """
        Test __eq__() with a int arg
        """
        self.assertTrue(self.node.uid == int("f9b8b725655d34a49328e659985bc43995caeec537f01f6129ce759ccd143119", 16))

class UidValueOperationTest(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.ip = "127.0.0.1"
        self.port = 5000
        self.node = chord.LocalNode(self.ip, self.port, _stabilizer=False)

    @classmethod
    def tearDownClass(self):
        self.node.stopXmlRPCServer()

    def test_add_int(self):
        """
        Test __add__() with int arg
        Test if len(result) == 64
        
        Note: Test will failed if self.node.uid.value is '64 * "f"'
        """
        self.assertEqual(
                int(self.node.uid + 1, 16),
                int(self.node.uid.value, 16) + 1
        )
        self.assertEqual(len(self.node.uid + int(1)), 64)

    def test_add_str(self):
        """
        Test __add__() with str arg
        
        Note: assertEqual on operation result will failed if self.node.uid.value is '64 * "f"'

        """
        self.assertEqual(
                int(self.node.uid + str("1".zfill(64)), 16),
                int(self.node.uid.value, 16) + 1
        )
        self.assertEqual(len(self.node.uid + str("1".zfill(64))), 64)

    def test_add_str_endOfRing(self):
        """
        Test __add__() with str arg in case result of __add__ go above "f"*64
        
        """
        self.node.uid.setValue("e".rjust(64, "f"))
        # Add 2 to the previous setValue then result should be "0"*64
        self.assertEqual(
                self.node.uid + str("2".zfill(64)),
                "0"*64
        )

    def test_sub_int(self):
        """
        Test __sub__() with int arg
        
        Note: Test will failed if self.node.uid.value is '64 * "0"'
        """
        self.assertEqual(
                int(self.node.uid - 1, 16),
                int(self.node.uid.value, 16) - 1
        )
        self.assertEqual(len(self.node.uid - int(1)), 64)

    def test_sub_str(self):
        """
        Test __sub__() with str arg
        
        Note: Test will failed if self.node.uid.value is '64 * "0"'

        """
        self.assertEqual(
                int(self.node.uid - str("1".zfill(64)), 16),
                int(self.node.uid.value, 16) - 1
        )
        self.assertEqual(len(self.node.uid - str("1".zfill(64))), 64)

    def test_sub_int_beginOfRing(self):
        """
        Test __sub__() with int arg
        
        """
        self.node.uid.setValue("1".rjust(64, "0"))
        self.assertEqual(
                self.node.uid - 2,
                "f"*64
        )
        self.assertEqual(len(self.node.uid - int(1)), 64)

class UidIsBetweenTest(unittest.TestCase):
    """
    Test isBetween method from Key class
    """

    @classmethod
    def setUpClass(self):
        self.ip = "127.0.0.1"
        self.port = 3000
        self.node0 = chord.LocalNode(self.ip, self.port, _stabilizer=False)

    @classmethod
    def tearDownClass(self):
        self.node0.stopXmlRPCServer()

    def test_isbetween(self):
        self.assertTrue(self.node0.uid.isbetween(64*"0", 64*"f"))
        self.assertFalse(self.node0.uid.isbetween(64*"f", 64*"0"))
        self.assertTrue(self.node0.uid.isbetween(
            "54e9cbfb5e6b16c5220a7468c86164b0abd629cc0d051cf989aad17a6d0896f9",
            "54e9cbfb5e6b16c5220a7468c86164b0abd629cc0d051cf989aad17a6d0896fb"
            )
        )
        self.assertFalse(self.node0.uid.isbetween(
            "54e9cbfb5e6b16c5220a7468c86164b0abd629cc0d051cf989aad17a6d0896fb",
            "54e9cbfb5e6b16c5220a7468c86164b0abd629cc0d051cf989aad17a6d0896f9"
            )
        )
        # The 2 next tests go above the ring limit ("f" * 64)
        # while still including the tested uid
        self.assertTrue(self.node0.uid.isbetween(
            "f"*64,
            hex(int(self.node0.uid.value, 16) + 1).strip("0x")
            )
        )
        self.assertTrue(self.node0.uid.isbetween(
            hex(int(self.node0.uid.value, 16) - 1).strip("0x"),
            "0" * 64
            )
        )

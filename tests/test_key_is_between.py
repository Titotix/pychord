import unittest
import key
import hashlib

class KeyIsBetweenTest(unittest.TestCase):
    """
    Test isBetween method from class Key
    """

    @classmethod
    def setUpClass(self):
        self.key_0 = key.Key("0"*64)
        self.key_1 = key.Key("1"*64)
        self.key_a = key.Key("a"*64)
        self.key_e = key.Key("e"*64)

    def test_is_inside_equal_limits(self):
        self.assertRaises(key.EqualLimitsError, self.key_0._is_inside, self.key_a, self.key_a)

    def test_is_between_r_inclu(self):
        self.assertTrue(self.key_a.is_between_r_inclu(self.key_0, self.key_e))
        self.assertTrue(self.key_a.is_between_r_inclu(self.key_1, self.key_0))
        self.assertTrue(self.key_a.is_between_r_inclu(self.key_0, self.key_a))
        self.assertFalse(self.key_a.is_between_r_inclu(self.key_a, self.key_e))
        self.assertFalse(self.key_a.is_between_r_inclu(self.key_e, self.key_1))

    def test_is_between_l_inclu(self):
        self.assertTrue(self.key_a.is_between_l_inclu(self.key_0, self.key_e))
        self.assertTrue(self.key_a.is_between_l_inclu(self.key_1, self.key_0))
        self.assertTrue(self.key_a.is_between_l_inclu(self.key_a, self.key_e))
        self.assertFalse(self.key_a.is_between_l_inclu(self.key_1, self.key_a))
        self.assertFalse(self.key_a.is_between_l_inclu(self.key_e, self.key_1))

    def test_is_between_inclu(self):
        self.assertTrue(self.key_a.is_between_inclu(self.key_0, self.key_e))
        self.assertTrue(self.key_a.is_between_inclu(self.key_1, self.key_0))
        self.assertTrue(self.key_a.is_between_inclu(self.key_a, self.key_e))
        self.assertTrue(self.key_a.is_between_inclu(self.key_1, self.key_a))
        self.assertFalse(self.key_a.is_between_inclu(self.key_e, self.key_1))

    def test_is_between_exclu(self):
        self.assertTrue(self.key_a.is_between_exclu(self.key_0, self.key_e))
        self.assertTrue(self.key_a.is_between_exclu(self.key_1, self.key_0))
        self.assertFalse(self.key_a.is_between_exclu(self.key_a, self.key_e))
        self.assertFalse(self.key_a.is_between_exclu(self.key_1, self.key_a))
        self.assertFalse(self.key_a.is_between_exclu(self.key_e, self.key_1))

    def test_is_inside(self):
        self.assertTrue(self.key_1._is_inside(64*"0", 64*"f"))
        self.assertFalse(self.key_1._is_inside(64*"f", 64*"0"))
        self.assertTrue(self.key_a._is_inside(
            "9" * 64,
            "{}{}".format("a"* 63,  "b")
            )
        )

        self.assertFalse(self.key_0._is_inside(
            "54e9cbfb5e6b16c5220a7468c86164b0abd629cc0d051cf989aad17a6d0896f9",
            "54e9cbfb5e6b16c5220a7468c86164b0abd629cc0d051cf989aad17a6d0896fb"
            )
        )
        # The 2 next tests go above the ring limit ("f" * 64)
        # while still including the tested uid
        self.assertTrue(self.key_0._is_inside(
            "f"*64,
            self.key_0.canonicalize(int(self.key_0.value, 16) + 1)
            )
        )
        self.assertTrue(self.key_1._is_inside(
            self.key_0.canonicalize(int(self.key_1.value, 16) - 1),
            "0" * 64
            )
        )

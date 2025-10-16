# test_discriminant.py
import unittest
from discriminant import calculate_discriminant


class TestDiscriminant(unittest.TestCase):

    def test_positive_discriminant(self):
        # Тест для случая, когда дискриминант больше нуля
        self.assertEqual(calculate_discriminant(1, -3, 2), 2)

    def test_zero_discriminant(self):
        # Тест для случая, когда дискриминант равен нулю
        self.assertEqual(calculate_discriminant(1, 2, 1), 0)

    def test_negative_discriminant(self):
        self.assertEqual(calculate_discriminant(1, 1, 1), -3)


if __name__ == "__main__":
    unittest.main()

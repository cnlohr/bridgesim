#!/usr/bin/env python

import unittest
from physics import *

class TestNVectors(unittest.TestCase):
  def setUp(self):
    self.v11  = NVector(1, 1)
    self.v22  = NVector(2, 2)
    self.v34  = NVector(3, 4)
    self.v10  = NVector(10, 0)
    self.vneg = NVector(-2, -2)

  def test_dimensionality(self):
    """Test counting of number of dimensionality"""
    self.assertEqual(self.v11.dimensionality(), 2)

  def test_magnitude(self):
    """Test magnitude calculation"""
    self.assertEqual(self.v34.magnitude(), 5)

  def test_norm(self):
    """Test unit vector calculation"""
    self.assertEqual(self.v10.norm(), NVector(1, 0))
    self.assertEqual(self.v11.norm(),
        NVector(0.7071067811865475, 0.7071067811865475))

  def test_dot(self):
    """Test dot product calculation"""
    self.assertEqual(self.v22.dot(self.v34), 14)

    with self.assertRaises(DimensionalityError):
      NVector(2, 2).dot(NVector(3, 3, 3))

  def test_init(self):
    """Check initialization"""
    self.assertEqual(self.v11.dimensions,  (1, 1))
    self.assertEqual(self.v34.dimensions,  (3, 4))
    self.assertEqual(self.vneg.dimensions, (-2, -2))

  def test_equality(self):
    """Check equality between vectors"""
    self.assertEqual(NVector(5, 5), NVector(5, 5))
    self.assertNotEqual(NVector(3, 4), NVector(4, 3))

  def test_neg(self):
    """Check negation"""
    self.assertEqual(NVector(1, -1), -NVector(-1, 1))
    self.assertNotEqual(NVector(10, 5), -NVector(10, 5))

  def test_truth(self):
    """Check truth values"""
    self.assertFalse(NVector(0, 0, 0, 0))
    self.assertTrue(NVector(1, 0))
    self.assertTrue(NVector(-10, -20, -30))

  def test_addition(self):
    """Check vector addition"""
    self.assertEqual(NVector(3, 2, 1, 0) + NVector(0, 1, 2, 3),
        NVector(3, 3, 3, 3))
    
    # Make sure some exceptions are raised.
    with self.assertRaises(DimensionalityError):
      NVector(2, 2) + NVector(3, 3, 3)
    with self.assertRaises(TypeError):
      NVector(1, 1) + 10

  def test_subtraction(self):
    """Check vector subtraction"""
    self.assertEqual(NVector(3, 2, 1, 0) - NVector(0, 1, 2, 3),
        NVector(3, 1, -1, -3))
    
    # Make sure some exceptions are raised.
    with self.assertRaises(DimensionalityError):
      NVector(2, 2) - NVector(3, 3, 3)
    with self.assertRaises(TypeError):
      NVector(1, 1) - 10

  def test_multiplication(self):
    """Check vector and scalar multiplication"""
    self.assertEqual(NVector(4, 2) * 10, NVector(40, 20))
    self.assertEqual(2 * NVector(1, 1), NVector(2, 2))
    self.assertEqual(NVector(3, 3) * NVector(2, 2), NVector(6, 6))

    # Make sure some exceptions are raised.
    with self.assertRaises(DimensionalityError):
      NVector(1) * NVector(2, 2)

  def test_division(self):
    """Check vector and scalar true and floor division"""
    self.assertEqual(NVector(5, 5) / NVector(2, 2), NVector(2.5, 2.5))
    self.assertEqual(NVector(5, 5) // NVector(2, 2), NVector(2, 2))

    self.assertEqual(NVector(5, 5) / 2, NVector(2.5, 2.5))
    self.assertEqual(NVector(5, 5) // 2, NVector(2, 2))

    with self.assertRaises(DimensionalityError):
      NVector(3, 3, 3) / NVector(2, 2)

    with self.assertRaises(DimensionalityError):
      NVector(3, 3, 3) // NVector(2, 2)

    with self.assertRaises(TypeError):
      5 / NVector(1, 1)

    with self.assertRaises(TypeError):
      5 // NVector(1, 1)

  def test_stringy(self):
    """Test string formatting"""
    self.assertEqual(str(NVector(1, 1)), "<1.000000, 1.000000>")

class TestVectors(unittest.TestCase):
  def setUp(self):
    self.v0   = Vector()
    self.v333 = Vector(3, 3, 3)
    self.v234 = Vector(2, 3, 4)

  def test_cross(self):
    self.assertEqual(Vector(5, 0, 0).cross(Vector(0, 5, 0)),
        Vector(0, 0, 25))

    self.assertEqual(Vector(0, 5, 0).cross(Vector(5, 0, 0)),
        Vector(0, 0, -25))

if __name__ == "__main__":
  unittest.main()

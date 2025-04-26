#!/usr/bin/env python3
"""
Tests for the Nakamoto coefficient computation module.
"""

import os
import unittest
import pandas as pd
import tempfile
import json
from pathlib import Path

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.compute_nakamoto import compute_nakamoto_coefficient, compute_eip_nakamoto


class TestNakamotoCoefficient(unittest.TestCase):
    """Test cases for Nakamoto coefficient computations."""

    def test_compute_nakamoto_coefficient_basic(self):
        """Test basic Nakamoto coefficient computation."""
        # Create a test DataFrame
        data = {
            'Entity': ['A', 'B', 'C', 'D', 'E'],
            'Share': [0.3, 0.25, 0.2, 0.15, 0.1]
        }
        df = pd.DataFrame(data)
        
        # Compute Nakamoto coefficient with threshold 0.5
        result = compute_nakamoto_coefficient(df, 'Entity', 'Share', 0.5)
        
        # It should take 3 entities (A + B + C = 0.75) to exceed 0.5
        self.assertEqual(result, 3)
        
    def test_compute_nakamoto_coefficient_equal_shares(self):
        """Test Nakamoto coefficient with equal shares."""
        # Create a test DataFrame with equal shares
        data = {
            'Entity': ['A', 'B', 'C', 'D', 'E'],
            'Share': [0.2, 0.2, 0.2, 0.2, 0.2]
        }
        df = pd.DataFrame(data)
        
        # Compute Nakamoto coefficient with threshold 0.5
        result = compute_nakamoto_coefficient(df, 'Entity', 'Share', 0.5)
        
        # It should take 3 entities to exceed 0.5
        self.assertEqual(result, 3)
        
    def test_compute_nakamoto_coefficient_high_concentration(self):
        """Test Nakamoto coefficient with high concentration."""
        # Create a test DataFrame with one dominant entity
        data = {
            'Entity': ['A', 'B', 'C', 'D', 'E'],
            'Share': [0.6, 0.1, 0.1, 0.1, 0.1]
        }
        df = pd.DataFrame(data)
        
        # Compute Nakamoto coefficient with threshold 0.5
        result = compute_nakamoto_coefficient(df, 'Entity', 'Share', 0.5)
        
        # It should take only 1 entity to exceed 0.5
        self.assertEqual(result, 1)
        
    def test_compute_eip_nakamoto(self):
        """Test EIP Nakamoto coefficient computation."""
        # Create a test DataFrame mimicking the authors.csv format
        data = {
            'EIP': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            'Title': ['Title1', 'Title2', 'Title3', 'Title4', 'Title5', 
                      'Title6', 'Title7', 'Title8', 'Title9', 'Title10'],
            'Status': ['Final', 'Final', 'Draft', 'Final', 'Living', 
                       'Draft', 'Final', 'Last Call', 'Draft', 'Final'],
            'Organization': ['Org1', 'Org2', 'Org3', 'Org1', 'Org2', 
                            'Org3', 'Org1', 'Org2', 'Org3', 'Org4']
        }
        df = pd.DataFrame(data)
        
        # Compute EIP Nakamoto coefficient
        result = compute_eip_nakamoto(df)
        
        # There are 7 accepted EIPs (Final, Living, Last Call)
        # Org1: 3, Org2: 3, Org4: 1
        # So the Nakamoto coefficient should be 2 (Org1 + Org2 = 6/7)
        self.assertEqual(result, 2)


if __name__ == "__main__":
    unittest.main() 
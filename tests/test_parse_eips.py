#!/usr/bin/env python3
"""
Tests for the EIP parser module.
"""

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, mock_open

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.parse_eips import parse_eip_file, EipAuthor, EipMetadata


class TestEipParser(unittest.TestCase):
    """Test cases for the EIP parser."""

    def test_parse_eip_file_valid(self):
        """Test parsing a valid EIP file."""
        mock_eip_content = """---
eip: 1
title: EIP Purpose and Guidelines
description: Guidelines for creating and submitting an EIP
author: Martin Becze <mb@ethereum.org>, Hudson Jameson <hudson@ethereum.org>
status: Living
type: Meta
created: 2015-10-27
---

## Abstract
This document describes the EIP process...
"""
        mock_path = Path("eip-1.md")
        
        with patch("builtins.open", mock_open(read_data=mock_eip_content)):
            result = parse_eip_file(mock_path)
            
        self.assertIsNotNone(result)
        self.assertEqual(result.eip_number, 1)
        self.assertEqual(result.title, "EIP Purpose and Guidelines")
        self.assertEqual(result.status, "Living")
        self.assertEqual(result.type, "Meta")
        self.assertEqual(len(result.authors), 2)
        
        self.assertEqual(result.authors[0].name, "Martin Becze")
        self.assertEqual(result.authors[0].email, "mb@ethereum.org")
        
        self.assertEqual(result.authors[1].name, "Hudson Jameson")
        self.assertEqual(result.authors[1].email, "hudson@ethereum.org")

    def test_parse_eip_file_with_github_handles(self):
        """Test parsing an EIP file with GitHub handles."""
        mock_eip_content = """---
eip: 20
title: Token Standard
author: Fabian Vogelsteller @frozeman, Vitalik Buterin <vitalik@ethereum.org> (Ethereum Foundation)
status: Final
type: Standards Track
category: ERC
created: 2015-11-19
---

## Abstract
A standard interface for tokens...
"""
        mock_path = Path("eip-20.md")
        
        with patch("builtins.open", mock_open(read_data=mock_eip_content)):
            result = parse_eip_file(mock_path)
            
        self.assertIsNotNone(result)
        self.assertEqual(result.eip_number, 20)
        self.assertEqual(len(result.authors), 2)
        
        self.assertEqual(result.authors[0].name, "Fabian Vogelsteller")
        self.assertEqual(result.authors[0].github, "frozeman")
        
        self.assertEqual(result.authors[1].name, "Vitalik Buterin")
        self.assertEqual(result.authors[1].email, "vitalik@ethereum.org")
        self.assertEqual(result.authors[1].organization, "Ethereum Foundation")

    def test_parse_eip_file_invalid_format(self):
        """Test parsing an invalid EIP file."""
        mock_eip_content = """
# This is not a valid EIP format
No YAML frontmatter here.
"""
        mock_path = Path("invalid.md")
        
        with patch("builtins.open", mock_open(read_data=mock_eip_content)):
            result = parse_eip_file(mock_path)
            
        self.assertIsNone(result)

    def test_parse_eip_file_invalid_filename(self):
        """Test parsing a file with an invalid filename format."""
        mock_eip_content = """---
eip: 1
title: Test
author: Test Author
status: Draft
type: Meta
created: 2022-01-01
---
"""
        mock_path = Path("not-an-eip-file.md")
        
        with patch("builtins.open", mock_open(read_data=mock_eip_content)):
            result = parse_eip_file(mock_path)
            
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main() 
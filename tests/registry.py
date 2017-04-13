# -*- coding: utf-8 -*-
"""Tests for the definitions registry."""

import unittest

from dtfabric import definitions
from dtfabric import registry

from tests import test_lib


class DataTypeDefinitionsRegistryTest(test_lib.BaseTestCase):
  """Data type definitions registry tests."""

  def testRegistration(self):
    """Tests the RegisterDefinition and DeregisterDefinition functions."""
    definitions_registry = registry.DataTypeDefinitionsRegistry()

    data_type_definition = definitions.IntegerDefinition(
        u'int32', aliases=[u'LONG', u'LONG32'],
        description=u'signed 32-bit integer')

    definitions_registry.RegisterDefinition(data_type_definition)

    with self.assertRaises(KeyError):
      definitions_registry.RegisterDefinition(data_type_definition)

    test_definition = definitions.IntegerDefinition(
        u'LONG', description=u'long integer')

    with self.assertRaises(KeyError):
      definitions_registry.RegisterDefinition(test_definition)

    test_definition = definitions.IntegerDefinition(
        u'test', aliases=[u'LONG'], description=u'long integer')

    with self.assertRaises(KeyError):
      definitions_registry.RegisterDefinition(test_definition)

    definitions_registry.DeregisterDefinition(data_type_definition)

    with self.assertRaises(KeyError):
      definitions_registry.DeregisterDefinition(data_type_definition)

  def testGetDefinitionByName(self):
    """Tests the GetDefinitionByName function."""
    definitions_registry = registry.DataTypeDefinitionsRegistry()

    data_type_definition = definitions.IntegerDefinition(
        u'int32', aliases=[u'LONG', u'LONG32'],
        description=u'signed 32-bit integer')

    definitions_registry.RegisterDefinition(data_type_definition)

    test_definition = definitions_registry.GetDefinitionByName(u'int32')
    self.assertIsNotNone(test_definition)
    self.assertIsInstance(test_definition, definitions.IntegerDefinition)

    test_definition = definitions_registry.GetDefinitionByName(u'LONG32')
    self.assertIsNotNone(test_definition)
    self.assertIsInstance(test_definition, definitions.IntegerDefinition)

    test_definition = definitions_registry.GetDefinitionByName(u'bogus')
    self.assertIsNone(test_definition)

    definitions_registry.DeregisterDefinition(data_type_definition)

  def testGetDefinitions(self):
    """Tests the GetDefinitions function."""
    definitions_registry = registry.DataTypeDefinitionsRegistry()

    test_definitions = definitions_registry.GetDefinitions()
    self.assertEqual(len(test_definitions), 0)

    data_type_definition = definitions.IntegerDefinition(
        u'int32', aliases=[u'LONG', u'LONG32'],
        description=u'signed 32-bit integer')

    definitions_registry.RegisterDefinition(data_type_definition)

    test_definitions = definitions_registry.GetDefinitions()
    self.assertEqual(len(test_definitions), 1)

    definitions_registry.DeregisterDefinition(data_type_definition)


if __name__ == '__main__':
  unittest.main()

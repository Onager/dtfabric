# -*- coding: utf-8 -*-
"""The definition reader objects."""

import abc
import glob
import os
import yaml

from dtfabric import definitions
from dtfabric import errors


class DataTypeDefinitionsReader(object):
  """Class that defines the data type definitions reader interface."""

  @abc.abstractmethod
  def ReadDefinitionFromDict(self, definition_values):
    """Reads a data type definition from a dictionary.

    Args:
      definition_values (dict[str, object]): definition values.

    Returns:
      DataTypeDefinition: data type definition.

    Raises:
      FormatError: if the definitions values are missing or if the format is
          incorrect.
    """


class DataTypeDefinitionsFileReader(DataTypeDefinitionsReader):
  """Class that defines the data type definitions file reader interface."""

  def _ReadStructureMember(self, definition_values):
    """Reads a structure member definition.

    Args:
      definition_values (dict[str, object]): definition values.
      definition_object (DataTypeDefinition): data type definition.
      name (str): name of the definition.

    Returns:
      StructureMemberDefinition: structure attribute definition.

    Raises:
      FormatError: if the definitions values are missing or if the format is
          incorrect.
    """
    if not definition_values:
      raise errors.FormatError(u'Missing definition values.')

    name = definition_values.get(u'name', None)
    sequence = definition_values.get(u'sequence', None)
    union = definition_values.get(u'union', None)

    if not name and not sequence and not union:
      raise errors.FormatError(
          u'Invalid structure attribute definition missing name, sequence or '
          u'union.')

    aliases = definition_values.get(u'aliases', None)
    data_type = definition_values.get(u'data_type', None)
    description = definition_values.get(u'description', None)

    return definitions.StructureMemberDefinition(
        name, aliases=aliases, data_type=data_type, description=description)

  def _ReadStructureMembers(
      self, definition_values, definition_object, name):
    """Reads structure members definitions.

    Args:
      definition_values (dict[str, object]): definition values.
      definition_object (DataTypeDefinition): data type definition.
      name (str): name of the definition.
    """
    for attribute in definition_values:
      structure_attribute = self._ReadStructureMember(attribute)
      definition_object.members.append(structure_attribute)

  def ReadDefinitionFromDict(self, definition_values):
    """Reads a data type definition from a dictionary.

    Args:
      definition_values (dict[str, object]): definition values.

    Returns:
      DataTypeDefinition: data type definition.

    Raises:
      FormatError: if the definitions values are missing or if the format is
          incorrect.
    """
    if not definition_values:
      raise errors.FormatError(u'Missing definition values.')

    name = definition_values.get(u'name', None)
    if not name:
      raise errors.FormatError(u'Invalid definition missing name.')

    type_indicator = definition_values.get(u'type', None)
    if not type_indicator:
      raise errors.FormatError(u'Invalid definition missing type.')

    aliases = definition_values.get(u'aliases', None)
    byte_order = definition_values.get(u'byte_order', None)
    description = definition_values.get(u'description', None)

    definition_object = definitions.StructureDefinition(
        name, aliases=aliases, byte_order=byte_order, description=description)

    members = definition_values.get(u'members')
    if members:
      self._ReadStructureMembers(members, definition_object, name)

    return definition_object

  def ReadDirectory(self, path, extension=None):
    """Reads data type definitions from a directory.

    This function does not recurse sub directories.

    Args:
      path (str): path of the directory to read from.
      extension (Optional[str]): extension of the filenames to read.

    Yields:
      DataTypeDefinition: data type definition.
    """
    if extension:
      glob_spec = os.path.join(path, u'*.{0:s}'.format(extension))
    else:
      glob_spec = os.path.join(path, u'*')

    for definition_file in glob.glob(glob_spec):
      for definition_object in self.ReadFile(definition_file):
        yield definition_object

  def ReadFile(self, path):
    """Reads data type definitions from a file.

    Args:
      path (str): path of the file to read from.

    Yields:
      DataTypeDefinition: data type definition.
    """
    with open(path, 'r') as file_object:
      for definition_object in self.ReadFileObject(file_object):
        yield definition_object

  @abc.abstractmethod
  def ReadFileObject(self, file_object):
    """Reads data type definitions from a file-like object.

    Args:
      file_object (file): file-like object to read from.

    Yields:
      DataTypeDefinition: data type definition.
    """


class YAMLDataTypeDefinitionsFileReader(DataTypeDefinitionsFileReader):
  """Class that implements the YAML data type definitions file reader."""

  def ReadFileObject(self, file_object):
    """Reads data type definitions from a file-like object.

    Args:
      file_object (file): file-like object to read from.

    Yields:
      DataTypeDefinition: data type definition.
    """
    yaml_generator = yaml.safe_load_all(file_object)

    last_definition_object = None
    for yaml_definition in yaml_generator:
      try:
        definition_object = self.ReadDefinitionFromDict(yaml_definition)

      except errors.FormatError as exception:
        if last_definition_object:
          error_location = u'After: {0:s}'.format(last_definition_object.name)
        else:
          error_location = u'At start'

        raise errors.FormatError(u'{0:s} {1:s}'.format(
            error_location, exception))

      yield definition_object
      last_definition_object = definition_object

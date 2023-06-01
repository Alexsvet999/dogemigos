import pytest

from dogemigos.metadata import Metadata

__author__ = "ipdoe"
__copyright__ = "ipdoe"
__license__ = "MPL-2.0"


def test_attributes():
    revealed = Metadata.MAX_SUPPLY - 35
    all_attributes = Metadata.read_attributes_from_raw_metadata()
    for a in all_attributes:
        attribute_sum = 0
        for trait in all_attributes[a]:
            attribute_sum += all_attributes[a][trait]
        assert attribute_sum == revealed



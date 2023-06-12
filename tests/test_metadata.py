import pytest

from dogemigos.metadata import Metadata

def test__read_attributes_from_raw_metadata():
    revealed = Metadata.MAX_SUPPLY - 35
    all_attributes = Metadata.read_attributes_from_raw_metadata()
    for a in all_attributes:
        attribute_sum = 0
        for trait in all_attributes[a]:
            attribute_sum += all_attributes[a][trait]

        if a == "Not Revealed":
            assert attribute_sum == 35
        else:
            assert attribute_sum == revealed


def test__read_doge_types_from_raw_metadata():
    def test_doge_types(types):
        assert len(types["Twins"]) == 7
        assert len(types["Trait count 7"]) == 2
        assert len(types["Legendary"]) == 20
        assert len(types["Full Body Suit"]) == 16
        assert len(types["Body"]) == 4
        assert len(types["Body"]["Alien"]) == 248
        assert len(types["Body"]["Robot"]) == 249
        assert len(types["Body"]["Demon"]) == 249
        assert len(types["Body"]["Zombie"]) == 249

    types = Metadata.read_doge_types_from_raw_metadata()
    test_doge_types(types)

    types = Metadata.get_doge_types()
    test_doge_types(types)

import pytest

from dogemigos.lib.metadata import DogemigosMetadata

def test__read_attributes_from_raw_metadata():
    revealed = DogemigosMetadata.MAX_SUPPLY - 35
    all_attributes = DogemigosMetadata.read_attributes_from_raw_metadata()
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

    types = DogemigosMetadata.read_doge_types_from_raw_metadata()
    test_doge_types(types)

    types = DogemigosMetadata.get_doge_types()
    test_doge_types(types)

def test__calculate_open_rarity():
    def test_rarity(metadata):
        assert metadata["1"]["open_rarity_rank"] == 6395
        assert metadata["1"]["open_rarity_score"] == 0.6767607144247997
        assert metadata["3000"]["open_rarity_rank"] == 2692
        assert metadata["3000"]["open_rarity_score"] == 1.0121343668279381
        assert metadata["6666"]["open_rarity_rank"] == 2944
        assert metadata["6666"]["open_rarity_score"] == 0.9988720100401157

    metadata = DogemigosMetadata.calculate_open_rarity(DogemigosMetadata.get_raw())
    test_rarity(metadata)
    metadata = DogemigosMetadata.get_metadata()
    test_rarity(metadata)
import json
from pathlib import Path
from dogemigos import ROOT_PATH
from dogemigos.lib.contracts.dogemigos import ADDRESS

from w3f.lib.metadata import Metadata


def dump_json(target: Path, data: dict, indent=None):
    with open(target, 'w') as o:
        if indent is None:
            json.dump(data, o)
        else:
            o.write(json.dumps(data, indent=indent))

class DogemigosMetadata(Metadata):
    NAME = "Dogemigos"
    CONTRACT = ADDRESS
    MAX_SUPPLY = 6666
    OS_SLUG ="dogemigos-onchain"

    _DAT = ROOT_PATH / "dat/dogemigos"
    __NOT_REVEALED = "Not Revealed"
    _HASH = "bafybeidobz2qzgytkqwmb3iq2fdwxvndk3pri5dnyqqhp6df5cshqp6io4"
    _TYPES = ["Trait count 7", "Full Body Suit", "Legendary", "Alien", "Robot", "Demon", "Zombie"]

    class DogeTypes(dict):
        def to_string(self):
            lines = []
            lines.append("{")
            for t in self:
                _type = self[t]
                if t == "Body":
                    lines.append(f'  "{t}": {{')
                    for b in _type:
                        lines.append(f'    "{b}": {_type[b]},')
                    lines[-1] = lines[-1][:-1]
                    lines.append("  },")
                else:
                    lines.append(f'  "{t}": {json.dumps(_type)},')
            lines[-1] = lines[-1][:-1]
            lines.append("}")
            return '\n'.join(lines)

    @classmethod
    def _dump_nft_types(cls, types):
        with open(cls._nft_types(), 'w') as o:
            o.write(cls.DogeTypes(types).to_string())

    @classmethod
    def _get_attributes(cls, item_metadata: dict):
        try:
            return cls.Attributes(item_metadata["attributes"])
        except KeyError:
            return None

    @classmethod
    def _get_type(cls, item_metadata: dict) -> str:
        nft_attributes = cls._get_attributes(item_metadata)
        if nft_attributes is None:
            return None

        # Trait count 7
        if len(nft_attributes) == 7:
            return "Trait count 7"

        # Full Body Suits
        nft_type = nft_attributes.get("Full Body Suit")
        if (nft_type): return "Full Body Suit"

        # Legendary
        nft_type = nft_attributes.get("Legendary")
        if (nft_type): return "Legendary"

        # Bodies
        nft_type = nft_attributes.get("Body")
        if (nft_type): return nft_type

    @classmethod
    def _append_types(cls, id_str: str, item_metadata: dict, types: dict, no_dupes_set: set):
        nft_type = cls._get_type(item_metadata)
        if nft_type is None:
            return

        item_metadata["type"] = nft_type

        if nft_type in cls._TYPES:
            types.setdefault(cls._get_type(item_metadata), []).append(int(id_str))

        # Twins
        nft_attr_key = str(cls._get_attributes(item_metadata))
        if nft_attr_key in no_dupes_set:
            types.setdefault("Twins", {}).setdefault(no_dupes_set[nft_attr_key], []).append(id_str)
        else:
            no_dupes_set[nft_attr_key] = id_str

    @classmethod
    def read_doge_types_from_raw_metadata(cls):
        all_metadata = DogemigosMetadata.get_raw()
        types = cls.DogeTypes()
        no_dupes_set = {}

        for id in all_metadata:
            cls._append_types(id, all_metadata[id], types, no_dupes_set)

        return types

    @staticmethod
    def read(id, all_attributes) -> dict:
        pass

    @classmethod
    def _append_attributes(cls, id: str, item_metadata: dict, all_attributes: dict):
            asset_attributes = item_metadata.get("attributes",
                                                 [{"trait_type": f"{cls.__NOT_REVEALED}", "value": f"{cls.__NOT_REVEALED}"}])
            # Not revealed does not count as trait_count == 1
            if asset_attributes[0]["trait_type"] != cls.__NOT_REVEALED:
                asset_attributes.append({"trait_type": "trait_count", "value": len(asset_attributes)})

            for trait in asset_attributes:
                all_attributes.setdefault(trait["trait_type"], {trait["value"]: 0})
                all_attributes[trait["trait_type"]].setdefault(trait["value"], 0)

                all_attributes[trait["trait_type"]][trait["value"]] += 1

    @classmethod
    def _post_process_attributes(cls, attributes_hist: dict):
        revealed_cnt = cls.MAX_SUPPLY - attributes_hist[cls.__NOT_REVEALED][cls.__NOT_REVEALED]
        for attr in attributes_hist:
            attribute = attributes_hist[attr]
            sum = 0
            # Skip the not revealed meta attribute
            if attr != cls.__NOT_REVEALED:
                for trait in attribute:
                    sum += attribute[trait]

                # Skip if none == 0
                if revealed_cnt - sum > 0:
                    attribute["None"] = revealed_cnt - sum

        # Sort
        for attribute in attributes_hist:
            attr = dict(sorted(attributes_hist[attribute].items(), key=lambda item: item[1]))
            attributes_hist[attribute] = attr

        attributes_hist["Legendary"] = dict(sorted(attributes_hist["Legendary"].items()))
        attributes_hist["Full Body Suit"] = dict(sorted(attributes_hist["Full Body Suit"].items()))


    @classmethod
    def read_attributes_from_raw_metadata(cls) -> dict:
        raw_metadata = cls.get_raw()
        all_attributes = {}
        for id in raw_metadata:
            asset_attributes = raw_metadata[id].get("attributes",
                                                    [{"trait_type": f"{cls.__NOT_REVEALED}", "value": f"{cls.__NOT_REVEALED}"}])
            # Not revealed does not count as trait_count == 1
            if asset_attributes[0]["trait_type"] != cls.__NOT_REVEALED:
                asset_attributes.append({"trait_type": "trait_count", "value": len(asset_attributes)})

            for trait in asset_attributes:
                all_attributes.setdefault(trait["trait_type"], {trait["value"]: 0})
                all_attributes[trait["trait_type"]].setdefault(trait["value"], 0)

                all_attributes[trait["trait_type"]][trait["value"]] += 1

        revealed_cnt = cls.MAX_SUPPLY - all_attributes[cls.__NOT_REVEALED][cls.__NOT_REVEALED]

        for attr in all_attributes:
            attribute = all_attributes[attr]
            sum = 0
            # Skip the not revealed meta attribute
            if attr != cls.__NOT_REVEALED:
                for trait in attribute:
                    sum += attribute[trait]

                # Skip if none == 0
                if revealed_cnt - sum > 0:
                    attribute["None"] = revealed_cnt - sum

        # Sort
        for attribute in all_attributes:
            attr = dict(sorted(all_attributes[attribute].items(), key=lambda item: item[1]))
            all_attributes[attribute] = attr

        all_attributes["Legendary"] = dict(sorted(all_attributes["Legendary"].items()))
        all_attributes["Full Body Suit"] = dict(sorted(all_attributes["Full Body Suit"].items()))

        return all_attributes

    @classmethod
    def get_doge_types(cls):
        with open(cls._DOGE_TYPES, 'r') as f:
            return json.load(f)

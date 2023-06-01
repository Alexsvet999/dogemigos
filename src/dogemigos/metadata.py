import json
from pathlib import Path
from dogemigos import ROOT_PATH

def dump_json(target: Path, data: dict, indent=None):
    with open(target, 'w') as o:
        if indent is None:
            json.dump(data, o)
        else:
            o.write(json.dumps(data, indent=indent))

class Metadata:
    _HASH = "bafybeidobz2qzgytkqwmb3iq2fdwxvndk3pri5dnyqqhp6df5cshqp6io4"
    __DAT = ROOT_PATH / "dat"
    __NOT_REVEALED = "Not Revealed"
    _METADATA = __DAT / "metadata.json"
    _ATTRIBUTES = __DAT / "all_attributes_sorted.json"
    MAX_SUPPLY = 6666

    @classmethod
    def get_raw(cls) -> dict:
        with open(cls._METADATA, 'r') as f:
            return json.load(f)

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
    def dump_sorted_attributes(cls):
        dump_json(cls._ATTRIBUTES, cls.read_attributes_from_raw_metadata(), 2)

    @classmethod
    def get_attributes(cls) -> dict:
        with open(cls._ATTRIBUTES, 'r') as f:
            return json.load(f)
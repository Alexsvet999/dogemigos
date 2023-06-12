import json
from pathlib import Path
from dogemigos import ROOT_PATH
from open_rarity import StringAttribute

def dump_json(target: Path, data: dict, indent=None):
    with open(target, 'w') as o:
        if indent is None:
            json.dump(data, o)
        else:
            o.write(json.dumps(data, indent=indent))

class Metadata:
    _CONTRACT = "0x3C53941eE6a23a1A046F2a956BAF36e4E4b04E35"
    _HASH = "bafybeidobz2qzgytkqwmb3iq2fdwxvndk3pri5dnyqqhp6df5cshqp6io4"
    __DAT = ROOT_PATH / "dat"
    __NOT_REVEALED = "Not Revealed"
    _METADATA = __DAT / "metadata.json"
    _ATTRIBUTES = __DAT / "all_attributes_sorted.json"
    _DOGE_TYPES = __DAT / "doge_types.json"
    MAX_SUPPLY = 6666

    class Attributes(list):
        def has(self, trait, value):
            if {"trait_type": trait, "value": value} in self:
                return True
            return False

        def to_open_rarity(self):
            open_rarity_attr = {}
            for trait in self:
                open_rarity_attr[trait["trait_type"]] = StringAttribute(name=trait["trait_type"], value=trait["value"])
            return open_rarity_attr



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

        def dump(self):
            with open(Metadata._DOGE_TYPES, 'w') as o:
                o.write(self.to_string())

    @classmethod
    def get_raw(cls) -> dict:
        with open(cls._METADATA, 'r') as f:
            return json.load(f)

    @classmethod
    def read_doge_types_from_raw_metadata(cls):
        all_metadata = Metadata.get_raw()
        no_dupes_set = {}
        types = {}

        for id_str in all_metadata:
            id = int(id_str)
            metadata = all_metadata[id_str]
            try:
                nft_attributes = Metadata._Attributes(metadata["attributes"])
            except KeyError:
                continue

            # Bodies
            if nft_attributes.has("Body", "Alien"):
                types.setdefault("Body", {}).setdefault("Alien", []).append(id)
            elif nft_attributes.has("Body", "Robot"):
                types.setdefault("Body", {}).setdefault("Robot", []).append(id)
            elif nft_attributes.has("Body", "Demon "):
                types.setdefault("Body", {}).setdefault("Demon", []).append(id)
            elif nft_attributes.has("Body", "Zombie"):
                types.setdefault("Body", {}).setdefault("Zombie", []).append(id)

            # Twins
            nft_attr_key = str(nft_attributes) # Attributes dict to str
            if nft_attr_key in no_dupes_set:
                types.setdefault("Twins", {})[id] = no_dupes_set[nft_attr_key]
            else:
                no_dupes_set[nft_attr_key] = id

            # Full Body Suits
            if nft_attributes[0]["trait_type"] == "Full Body Suit":
                types.setdefault("Full Body Suit", []).append(id)

            # Legendary
            if nft_attributes[0]["trait_type"] == "Legendary":
                types.setdefault("Legendary", []).append(id)

            # Trait count 7
            if len(nft_attributes) == 7:
                types.setdefault("Trait count 7", []).append(id)

        return types

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
    def dump_sorted_attributes(cls):
        cls.DogeTypes(cls.read_doge_types_from_raw_metadata()).dump()

    @classmethod
    def get_attributes(cls) -> dict:
        with open(cls._ATTRIBUTES, 'r') as f:
            return json.load(f)

    @classmethod
    def get_doge_types(cls):
        with open(cls._DOGE_TYPES, 'r') as f:
            return json.load(f)

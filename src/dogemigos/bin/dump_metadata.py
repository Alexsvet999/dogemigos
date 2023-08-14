import dogemigos.lib.metadata as metadata
from w3f.lib.logger import to_json_str

print(metadata.DogemigosMetadata.NAME)
print(metadata.DogemigosMetadata._DAT)
print(metadata.DogemigosMetadata._raw_metadata())

metadata.DogemigosMetadata.redump()

# meta_data, types, attr = metadata.DogemigosMetadata.generate_metadata_from_raw()
# print(metadata.DogemigosMetadata.DogeTypes(types).to_string())
# print(to_json_str(attr))

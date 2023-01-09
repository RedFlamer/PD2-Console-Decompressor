import os
import zlib

# Header format
# uint32 total_uncompressed_size
# For every chunk:
# uint32 previous_chunk_size (once decompressed if last chunk was compressed, otherwise not present)
# uint32 chunk_size (size of next zlib chunk)

endian = "little"

for filename in os.scandir("./assets"):
    if filename.is_file() and (filename.path.find("_h.bundle") != -1 or filename.path.find("stream_") == -1 and filename.path.find("all_") == -1 and filename.path.find(".bundle") != 1): # package headers/data or all_x/stream_x headers
        print(filename.path)

        with open(filename.path, 'rb') as bundle, open(filename.path.replace("assets", "decompressed_assets"), 'wb') as new_bundle:
            total_decompressed_size = int.from_bytes(bundle.read(4), endian) # Total size once decompressed
            if total_decompressed_size == 0: # PS3 bundles start with 00 00 00 00
                endian = "big"
                total_decompressed_size = int.from_bytes(bundle.read(4), endian)
            else:
                bundle.read(4) # Size of previous (why?) zlib chunk once decompressed, ignored because it's not needed and isn't present for uncompressed chunks.

            while True:
                zlib_chunk_size = int.from_bytes(bundle.read(4), endian) # Size of next zlib chunk
                if not zlib_chunk_size:
                    break

                this_decompressed_size = zlib_chunk_size
                data = bundle.read(zlib_chunk_size)

                try:
                    data = zlib.decompress(data, wbits=zlib.MAX_WBITS|32)[:total_decompressed_size] # Trim off excess bytes from last chunk
                    new_bundle.write(data)
                    
                    this_decompressed_size = len(data)
                except zlib.error: # Uncompressed
                    new_bundle.write(data)

                total_decompressed_size -= this_decompressed_size

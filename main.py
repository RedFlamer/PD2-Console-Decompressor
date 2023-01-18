import os
import zlib

# Header:
# uint64 total_uncompressed_size
# For every chunk:
# uint32 compressed_chunk_size (size of next zlib chunk)
# byte[] chunk
# uint32 decompressed_chunk_size (present only if last chunk was compressed, always little endian)

DECOMPRESSED_CHUNK_SIZE = 2**16

for filename in os.scandir("./assets"):
    if filename.is_file() and (filename.path.find(".bundle") != -1 and filename.path.find("stream_") == -1 and filename.path.find("all_") == -1): # package headers/data or all_x/stream_x headers
        print(filename.path)

        with open(filename.path, 'rb') as bundle, open(filename.path.replace("assets", "decompressed_assets"), 'wb') as new_bundle:
            endian = "little"

            total_size_bytes = bundle.read(8) # Total size once decompressed
            total_size = int.from_bytes(total_size_bytes, endian)
            if total_size > 2**32: # Problematic if the package is >2^32 bytes once decompressed, but means big endian PS3/X360 bundles can be decompressed as well
                endian = "big"
                total_size = int.from_bytes(total_size_bytes, endian)

            while True:
                zlib_chunk_size = int.from_bytes(bundle.read(4), endian) # Size of next zlib chunk
                if not zlib_chunk_size:
                    break

                this_decompressed_size = zlib_chunk_size
                data = bundle.read(zlib_chunk_size)

                if zlib_chunk_size != DECOMPRESSED_CHUNK_SIZE: # Compressed chunk
                    data = zlib.decompress(data, wbits=zlib.MAX_WBITS|32, bufsize=DECOMPRESSED_CHUNK_SIZE)[:total_size]
                    this_decompressed_size = len(data) # Or use decompressed_chunk_size

                new_bundle.write(data)
                total_size -= this_decompressed_size
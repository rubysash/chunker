'''
# Chunk/Reassemble tool

Converts large file (any type) into json (hex) files
Reassembles all with checksum integrity checking
The json output is larger than the binary input, but compresses 
better than binary alone would most of the time

## to chunk into 3 MB at a time
python chunker.py chunk somefile.pdf 3

## To rebuild all chunks
python chunker.py reassemble somefile.pdf_metadata.json

## How it works
The somefile.pdf_metadata.json file it makes contains checksums on each json, 
and the original checksum so it can verify the rebuild:

### Example Metadata
```json
{
    "file_name": "CIS_Red_Hat_Enterprise_Linux_9_Benchmark_v2.0.0.pdf",
    "file_checksum": "b5bc38c11fad01c269af7367facee155",
    "chunks": [
        {
            "chunk_file": "CIS_Red_Hat_Enterprise_Linux_9_Benchmark_v2.0.0.pdf_01_03.json",
            "chunk_number": 1,
            "total_chunks": 3,
            "chunk_checksum": "8b438280fe32fd9df1e212280be081d6"
        },
        {
            "chunk_file": "CIS_Red_Hat_Enterprise_Linux_9_Benchmark_v2.0.0.pdf_02_03.json",
            "chunk_number": 2,
            "total_chunks": 3,
            "chunk_checksum": "2a11e0953b4ead663c948483c94d3995"
        },
        {
            "chunk_file": "CIS_Red_Hat_Enterprise_Linux_9_Benchmark_v2.0.0.pdf_03_03.json",
            "chunk_number": 3,
            "total_chunks": 3,
            "chunk_checksum": "e41e6684a571e7825815154eb581d097"
        }
    ]
}
```
### Example Json Chunk
The "chunks" are hex representations of binary data:

```json
{
    "file_name": "CIS_Red_Hat_Enterprise_Linux_9_Benchmark_v2.0.0.pdf",
    "chunk_number": 1,
    "total_chunks": 3,
    "chunk_checksum": "8b438280fe32fd9df1e212280be081d6",
    "chunk_data": "255044462d312....2f5469"
}
```
'''
import os
import hashlib
import json

def calculate_checksum(data):
    """Calculate the MD5 checksum of the provided data.
    
    Args:
        data (bytes): The data for which to calculate the checksum.

    Returns:
        str: The MD5 checksum as a hexadecimal string.
    """
    return hashlib.md5(data).hexdigest()

def chunk_file(input_file, chunk_size):
    """Chunk a file into smaller parts.

    Args:
        input_file (str): Path to the file to be chunked.
        chunk_size (int): Size of each chunk in bytes.

    Returns:
        list: A list of dictionaries containing metadata for each chunk.

    Creates JSON files for each chunk, containing metadata and chunk data in hex format.
    """
    file_size = os.path.getsize(input_file)
    total_chunks = (file_size + chunk_size - 1) // chunk_size

    chunk_metadata = []

    with open(input_file, 'rb') as f:
        for chunk_number in range(total_chunks):
            chunk_data = f.read(chunk_size)
            chunk_checksum = calculate_checksum(chunk_data)

            chunk_file_name = f"{os.path.basename(input_file)}_{chunk_number + 1:02d}_{total_chunks:02d}.json"
            chunk_metadata.append({
                "chunk_file": chunk_file_name,
                "chunk_number": chunk_number + 1,
                "total_chunks": total_chunks,
                "chunk_checksum": chunk_checksum,
            })

            # Create a JSON file for this chunk
            chunk_json = {
                "file_name": os.path.basename(input_file),
                "chunk_number": chunk_number + 1,
                "total_chunks": total_chunks,
                "chunk_checksum": chunk_checksum,
                "chunk_data": chunk_data.hex(),
            }

            with open(chunk_file_name, 'w') as chunk_file:
                json.dump(chunk_json, chunk_file, indent=4)

    return chunk_metadata

def create_metadata_file(input_file, chunk_metadata):
    """Create a metadata file for the entire file and its chunks.

    Args:
        input_file (str): Path to the original file.
        chunk_metadata (list): Metadata for each chunk.

    Returns:
        str: The name of the metadata file created.

    The metadata file includes the original file's checksum and details of all chunks.
    """
    file_checksum = calculate_checksum(open(input_file, 'rb').read())
    metadata = {
        "file_name": os.path.basename(input_file),
        "file_checksum": file_checksum,
        "chunks": chunk_metadata,
    }

    metadata_file_name = f"{os.path.basename(input_file)}_metadata.json"
    with open(metadata_file_name, 'w') as metadata_file:
        json.dump(metadata, metadata_file, indent=4)

    return metadata_file_name

def reassemble_file(metadata_file):
    """Reassemble the original file from its chunks.

    Args:
        metadata_file (str): Path to the metadata file.

    The function verifies checksum integrity after reassembly and creates the reassembled file.
    """
    with open(metadata_file, 'r') as f:
        metadata = json.load(f)

    original_file_name = metadata['file_name']
    with open(f"reassembled_{original_file_name}", 'wb') as output_file:
        for chunk in metadata['chunks']:
            chunk_file_name = chunk['chunk_file']
            with open(chunk_file_name, 'r') as chunk_file:
                chunk_data = json.load(chunk_file)
                output_file.write(bytes.fromhex(chunk_data['chunk_data']))

    # Verify checksum of reassembled file
    reassembled_checksum = calculate_checksum(open(f"reassembled_{original_file_name}", 'rb').read())
    if reassembled_checksum == metadata['file_checksum']:
        print("Reassembly complete. Checksum verified.")
    else:
        print("Reassembly failed. Checksum mismatch.")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Chunk and reassemble files for email transmission.")
    parser.add_argument("mode", choices=["chunk", "reassemble"], help="Mode: 'chunk' to split a file, 'reassemble' to combine chunks.")
    parser.add_argument("input_file", help="Path to the input file or metadata file.")
    parser.add_argument("chunk_size", type=int, nargs='?', help="Size of each chunk in MB (required for 'chunk' mode).")

    args = parser.parse_args()

    if not args.mode or args.mode in ['--help', '?'] or not args.input_file:
        print("\nUsage Examples:")
        print("To chunk a file into 3MB parts: python chunkerv1.py chunk somefile.pdf 3")
        print("To reassemble the file: python chunkerv1.py reassemble somefile.pdf_metadata.json")
        print("The JSON will be larger than your binary chunk, but will compress better too")
        exit(0)

    if args.mode == "chunk":
        if not os.path.exists(args.input_file):
            print(f"Error: File {args.input_file} does not exist.")
            exit(1)
        if not args.chunk_size:
            print("Error: Chunk size must be specified in 'chunk' mode.")
            exit(1)

        # Convert chunk size from MB to bytes
        chunk_size_bytes = args.chunk_size * 1024 * 1024

        print(f"Chunking file: {args.input_file} into {args.chunk_size} MB ({chunk_size_bytes}-byte) chunks...")

        chunk_metadata = chunk_file(args.input_file, chunk_size_bytes)
        metadata_file_name = create_metadata_file(args.input_file, chunk_metadata)

        print(f"Chunking complete. Metadata file: {metadata_file_name}")

    elif args.mode == "reassemble":
        if not os.path.exists(args.input_file):
            print(f"Error: Metadata file {args.input_file} does not exist.")
            exit(1)

        print(f"Reassembling file using metadata: {args.input_file}...")
        reassemble_file(args.input_file)

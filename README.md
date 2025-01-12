# Chunk/Reassemble tool

## What it Does
- Converts large file (any type) into json (hex) files
- Adds reassembled_ as a prefix to the rebuilt file
- Reassembles all with checksum integrity checking
- JSON output is larger than the binary input, but compresses better than binary alone would most of the time

## Use Case
I was trying to send a pdf that was larger than email allowed and email was only way to get the pdf to it's destination.

In chunks, I could send it a chunk at a time and stay under the email limit.


## Syntax
### Chunk 3 MB at a time into JSON

`python chunker.py chunk somefile.pdf 3`

### Rebuild all JSON chunks
`python chunker.py reassemble somefile.pdf_metadata.json`

## How it works

The somefile.pdf_metadata.json file it makes contains checksums on each json and the original checksum so it can verify the rebuild:

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

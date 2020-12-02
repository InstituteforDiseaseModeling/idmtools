import argparse
import random
from logging import getLogger, basicConfig

CHUNK_GENERATION_SIZE = 1048576 * 4
basicConfig()
logger = getLogger()


def generate_chunk(filename: str, total_bytes: int):
    logger.info(f"Writing chunk of {total_bytes} to {filename}")
    with open(filename, 'wb') as out:
        total_written = 0
        while total_written < total_bytes:
            # Write in 1 mb segments
            if total_written + CHUNK_GENERATION_SIZE > total_bytes:
                ws = total_bytes - total_written
            else:
                ws = CHUNK_GENERATION_SIZE
            out.write(bytearray(random.getrandbits(8) for _ in range(ws)))
            total_written += CHUNK_GENERATION_SIZE


def generate_chunks(total_chunks: int, chunk_size: int, chunk_name: str):
    logger.info(f"Writing {total_chunks} chunks")
    for i in range(total_chunks):
        fn = chunk_name.format(idx=i)
        generate_chunk(fn, chunk_size)


if __name__ == "__main__":
    random.seed()
    parser = argparse.ArgumentParser()
    parser.add_argument("--chunk-size", default=1024 * 256, type=int)
    parser.add_argument("--chunks", default=100, type=int)
    parser.add_argument("--chunk-name", default="{idx:05d}.chunk")

    args = parser.parse_args()
    generate_chunks(args.chunks, args.chunk_size, args.chunk_name)

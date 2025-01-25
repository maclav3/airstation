# Source: https://forum.micropython.org/viewtopic.php?t=7228&start=10

from flashbdev import bdev

def check():
    buf = bytearray(16)
    bdev.readblocks(0, buf)
    if buf[3:8] == b'MSDOS':
        return 'FAT'
    if buf[8:16] == b'littlefs':
        return 'littlefs'
    return 'unknown'

def dump(line_count=4, chunk_size=16):
    buf = bytearray(chunk_size)
    for block_num in range(line_count):
        offset = block_num * chunk_size
        print('%04x - %04x' % (offset, offset + chunk_size - 1), end=' - ')
        bdev.readblocks(block_num, buf)
        print(' '.join('%02x' % char for char in buf), end=' - ')
        print(''.join(chr(char) if 32 < char < 127 else '.' for char in buf))

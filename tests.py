import pytest
from DeflateCompressor import DeflateCompressor

class Test:
    def compressed_decompressed(self, file):
        with open(file, 'rb') as f:
            data = f.read()
        compressed = DeflateCompressor().compress(data)
        decompressed = DeflateCompressor().decompress(compressed)[:-1]
        assert decompressed == data

    def test(self):
        self.compressed_decompressed('spongebob.jpeg')
from LZ77Compressor import LZ77
from HuffmanCompressor import Huffman


class DeflateCompressor:
    def __init__(self):
        self.lz77 = LZ77()
        self.huffman = Huffman()

    def compress(self, data):
        compressed = self.huffman.compress(self.lz77.compress(data))
        return compressed


    def decompress(self, compressed_serialized_data):
        decompressed = self.lz77.decompress(self.huffman.decompress(compressed_serialized_data))
        return decompressed

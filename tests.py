from DeflateCompressor import DeflateCompressor


class Test:
    def compressed_decompressed(self, file):
        with open(file, 'rb') as f:
            data = f.read()
        compressed = DeflateCompressor().compress(data)
        decompressed = DeflateCompressor().decompress(compressed)
        assert decompressed == data
        print(len(compressed) / len(data))

    def test_files(self):
        self.compressed_decompressed('spongebob.jpeg')

    def test_text_harry_potter(self):
        self.compressed_decompressed('HarryPotterText.txt')

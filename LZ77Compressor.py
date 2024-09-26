class LZ77:
    def __init__(self, window_size=32768, buffer_size=256):
        self.window_size = window_size
        self.buffer_size = buffer_size

    def compress(self, data: bytes) -> bytes:
        compressed_data = bytearray()
        i = 0

        while i < len(data):
            match_length = 0
            match_distance = 0

            start_index = max(0, i - self.window_size)
            search_window = data[start_index:i]

            for j in range(len(search_window)):
                length = 0
                while length < self.buffer_size and (i + length < len(data)) and search_window[
                                                                                 j:j + length + 1] == data[
                                                                                                      i:i + length + 1]:
                    length += 1

                if length > match_length:
                    match_length = length
                    match_distance = len(search_window) - j

            if match_length > 0:
                compressed_data.extend(match_distance.to_bytes(2, byteorder='big'))
                compressed_data.append(match_length)

                if i + match_length < len(data):
                    compressed_data.append(data[i + match_length])
                else:
                    compressed_data.append(0)

                i += match_length + 1
            else:
                compressed_data.extend((0).to_bytes(2, byteorder='big'))
                compressed_data.append(0)
                compressed_data.append(data[i])
                i += 1

        return bytes(compressed_data)

    def decompress(self, compressed_data: bytes) -> bytes:
        decompressed_data = bytearray()
        i = 0

        while i < len(compressed_data):
            match_distance = int.from_bytes(compressed_data[i:i + 2], byteorder='big')
            match_length = compressed_data[i + 2]
            next_byte = compressed_data[i + 3]
            i += 4

            if match_distance > 0 and match_length > 0:
                start_index = len(decompressed_data) - match_distance
                decompressed_data.extend(decompressed_data[start_index:start_index + match_length])

            decompressed_data.append(next_byte)

        return bytes(decompressed_data)


if __name__ == '__main__':
    data = b"abracadabraabracadabra"
    lz77 = LZ77(window_size=32768, buffer_size=256)
    compressed = lz77.compress(data)
    print("Сжатые данные (в байтах):", compressed)
    decompressed = lz77.decompress(compressed)
    print("Восстановленные данные:", decompressed)

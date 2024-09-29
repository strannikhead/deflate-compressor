import struct


class LZ77:
    def __init__(self, window_size=32768, lookahead_buffer_size=255):
        self.window_size = window_size
        self.lookahead_buffer_size = lookahead_buffer_size

    def compress(self, data):
        i = 0
        output = bytearray()

        while i < len(data):
            match = self._find_longest_match(data, i)

            if match:
                (best_match_distance, best_match_length) = match
                next_symbol = data[i + best_match_length] if (i + best_match_length) < len(data) else 0
                packed_data = struct.pack('>HBB', best_match_distance, best_match_length, next_symbol)
                output.extend(packed_data)
                i += best_match_length + 1
            else:
                packed_data = struct.pack('>HBB', 0, 0, data[i])
                output.extend(packed_data)
                i += 1

        return bytes(output)

    def decompress(self, compressed_data):
        i = 0
        decompressed_data = bytearray()

        while i < len(compressed_data):
            (offset, length, symbol) = struct.unpack('>HBB', compressed_data[i:i + 4])
            i += 4

            if offset > 0 and length > 0:
                start = len(decompressed_data) - offset
                for _ in range(length):
                    decompressed_data.append(decompressed_data[start])
                    start += 1

            decompressed_data.append(symbol)

        return bytes(decompressed_data)

    def _find_longest_match(self, data, current_position):
        end_of_buffer = min(current_position + self.lookahead_buffer_size, len(data))

        best_match_distance = 0
        best_match_length = 0

        window_start = max(0, current_position - self.window_size)
        window = data[window_start:current_position]

        for length in range(1, end_of_buffer - current_position + 1):
            substring = data[current_position:current_position + length]
            pos = window.rfind(substring)
            if pos != -1:
                best_match_distance = current_position - (window_start + pos)
                best_match_length = length
            else:
                break

        if best_match_distance > 0 and best_match_length > 0:
            return best_match_distance, best_match_length
        else:
            return None

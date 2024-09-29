import heapq
from collections import defaultdict
import pickle


class Node:
    def __init__(self, frequency, byte=None, left=None, right=None):
        self.frequency = frequency
        self.byte = byte
        self.left = left
        self.right = right

    def __lt__(self, other):
        return self.frequency < other.frequency


class Huffman:
    def __init__(self):
        self.codes = {}

    def _calculate_frequencies(self, data):
        frequencies = defaultdict(int)
        for byte in data:
            frequencies[byte] += 1
        return frequencies

    def _build_huffman_tree(self, frequencies):
        heap = [Node(freq, byte) for byte, freq in frequencies.items()]
        heapq.heapify(heap)

        while len(heap) > 1:
            node1 = heapq.heappop(heap)
            node2 = heapq.heappop(heap)
            merged = Node(node1.frequency + node2.frequency, left=node1, right=node2)
            heapq.heappush(heap, merged)

        return heap[0]

    def _generate_codes(self, node, current_code=""):
        if node is None:
            return

        if node.byte is not None:
            self.codes[node.byte] = current_code
            return

        self._generate_codes(node.left, current_code + "0")
        self._generate_codes(node.right, current_code + "1")

    def compress(self, data):
        frequencies = self._calculate_frequencies(data)

        huffman_tree = self._build_huffman_tree(frequencies)

        self._generate_codes(huffman_tree)

        encoded_data = ''.join(self.codes[byte] for byte in data)

        extra_padding = 8 - len(encoded_data) % 8
        if extra_padding != 8:
            encoded_data += '0' * extra_padding
        else:
            extra_padding = 0

        padded_info = "{0:08b}".format(extra_padding)
        encoded_data = padded_info + encoded_data

        compressed_data = bytearray()
        for i in range(0, len(encoded_data), 8):
            byte = encoded_data[i:i + 8]
            compressed_data.append(int(byte, 2))

        output = {
            'compressed_data': bytes(compressed_data),
            'codes': self.codes
        }

        return pickle.dumps(output)

    def decompress(self, compressed_serialized_data):
        input_data = pickle.loads(compressed_serialized_data)
        compressed_data = input_data['compressed_data']
        codes = input_data['codes']

        reverse_codes = {code: byte for byte, code in codes.items()}

        bit_string = ''
        for byte in compressed_data:
            bit_string += f"{byte:08b}"

        padded_info = bit_string[:8]
        extra_padding = int(padded_info, 2)

        bit_string = bit_string[8:]
        if extra_padding > 0:
            bit_string = bit_string[:-extra_padding]

        decoded_bytes = bytearray()
        current_code = ''
        for bit in bit_string:
            current_code += bit
            if current_code in reverse_codes:
                decoded_bytes.append(reverse_codes[current_code])
                current_code = ''

        return bytes(decoded_bytes)

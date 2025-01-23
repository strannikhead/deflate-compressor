import os
import json
import struct
import hashlib
import time

from LZ77Compressor import LZ77
from HuffmanCompressor import Huffman


def compute_sha256(data: bytes) -> str:
    hasher = hashlib.sha256()
    hasher.update(data)
    return hasher.hexdigest()


class DeflateCompressor:
    def __init__(self):
        self.lz77 = LZ77()
        self.huffman = Huffman()

    def compress(self, data):
        compressed_lz77 = self.lz77.compress(data)
        compressed = self.huffman.compress(compressed_lz77)
        return compressed

    def decompress(self, compressed_serialized_data):
        decompressed_huffman = self.huffman.decompress(compressed_serialized_data)
        decompressed = self.lz77.decompress(decompressed_huffman)
        return decompressed


class Archiver:
    def __init__(self, compressor):
        self.compressor = compressor

    def archive_files(self, file_paths, archive_name):
        """
        Архивирует файлы
        :param file_paths: список файлов
        :param archive_name: название архива
        :return: None
        """
        archive_data = {}
        metadata = {}

        for file_path in file_paths:
            if not os.path.isfile(file_path):
                print(f"Файл не найден: {file_path}")

            with open(file_path, 'rb') as f:
                data = f.read()

            compressed_data = self.compressor.compress(data)
            file_hash = compute_sha256(data)

            metadata[file_path] = {
                'original_size': len(data),
                'compressed_size': len(compressed_data),
                'algorithm': 'DeflateCompressor',
                'sha256': file_hash,
                'ctime': os.path.getctime(file_path) if hasattr(os.path, 'getctime') else time.time(),
                'mtime': os.path.getmtime(file_path)
            }

            archive_data[file_path] = compressed_data

            print(f"Файл сжат: {file_path}")

        metadata_json = json.dumps(metadata).encode('utf-8')
        metadata_size = len(metadata_json)

        with open(archive_name, 'wb') as archive_file:
            # Запись размера метаданных (4 байта)
            archive_file.write(struct.pack('>I', metadata_size))
            archive_file.write(metadata_json)

            for file_path, compressed_data in archive_data.items():
                file_path_bytes = file_path.encode('utf-8')
                file_path_length = len(file_path_bytes)
                compressed_length = len(compressed_data)

                # 1) Длина пути файла (4 байта)
                archive_file.write(struct.pack('>I', file_path_length))
                # 2) Сам путь
                archive_file.write(file_path_bytes)
                # 3) Длина сжатых данных (4 байта)
                archive_file.write(struct.pack('>I', compressed_length))
                # 4) Сжатые данные
                archive_file.write(compressed_data)

        print(f"Archive completed")

    def extract_archive(self, archive_name, output_dir):
        """
        Извлекает файлы из архива в папку `output_dir`.
        Восстанавливает время последней модификации и проверяет SHA256 для целостности.
        """
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        with open(archive_name, 'rb') as archive_file:
            metadata_size_bytes = archive_file.read(4)
            if len(metadata_size_bytes) < 4:
                raise EncodingWarning('Файл поврежден или не является архивом')
            metadata_size = struct.unpack('>I', metadata_size_bytes)[0]

            metadata_json = archive_file.read(metadata_size)
            metadata = json.loads(metadata_json.decode('utf-8'))

            for file_path, meta in metadata.items():
                path_length_bytes = archive_file.read(4)
                if len(path_length_bytes) < 4:
                    print("Архив поврежден при чтении длины пути файла.")
                    return
                path_length = struct.unpack('>I', path_length_bytes)[0]

                file_path_bytes = archive_file.read(path_length)
                extracted_file_path = file_path_bytes.decode('utf-8')

                compressed_length_bytes = archive_file.read(4)
                if len(compressed_length_bytes) < 4:
                    print("Архив поврежден при чтении длины сжатых данных.")
                    return
                compressed_length = struct.unpack('>I', compressed_length_bytes)[0]

                compressed_data = archive_file.read(compressed_length)
                decompressed_data = self.compressor.decompress(compressed_data)

                new_sha = compute_sha256(decompressed_data)
                if new_sha != meta['sha256']:
                    print(f"Ошибка целостности: {extracted_file_path}")
                    continue

                output_file_path = os.path.join(output_dir, extracted_file_path)
                output_file_dir = os.path.dirname(output_file_path)
                if not os.path.exists(output_file_dir):
                    os.makedirs(output_file_dir)

                with open(output_file_path, 'wb') as out_f:
                    out_f.write(decompressed_data)

                os.utime(output_file_path, (meta['mtime'], meta['mtime']))

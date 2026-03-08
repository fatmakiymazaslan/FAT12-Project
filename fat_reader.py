import struct
import math
import sys

class FAT12Reader:
    def __init__(self, image_path):
        self.image_path = image_path
        self.image = None
        self.boot_sector = {}
        self.fat_table = b""
        
    def open_image(self):
        """Disk imajını binary modda açar."""
        try:
            self.image = open(self.image_path, 'rb')
        except FileNotFoundError:
            print(f"Hata: {self.image_path} bulunamadı.")
            sys.exit(1)

    def parse_boot_sector(self):
        """Boot sector (ilk 512 bayt) verilerini ayrıştırır."""
        bs = self.image.read(512)
        # struct.unpack ile binary veriyi anlamlı değişkenlere dönüştürür
        unpacked = struct.unpack("<3x8s HBHBHHBHHHII B1xBI 11s8s", bs[:62])
        
        self.boot_sector = {
            "OEMName": unpacked[0].decode().strip(),
            "BytsPerSec": unpacked[1],
            "SecPerClus": unpacked[2],
            "RsvdSecCnt": unpacked[3],
            "NumFATs": unpacked[4],
            "RootEntCnt": unpacked[5],
            "TotSec16": unpacked[6],
            "FATSz16": unpacked[8],
            "VolLab": unpacked[16].decode().strip(),
            "FilSysType": unpacked[17].decode().strip()
        }
        
        # Önemli ofset hesaplamaları
        self.root_dir_start_sec = self.boot_sector["RsvdSecCnt"] + (self.boot_sector["NumFATs"] * self.boot_sector["FATSz16"])
        self.root_dir_start_byte = self.root_dir_start_sec * self.boot_sector["BytsPerSec"]
        
        root_dir_bytes = self.boot_sector["RootEntCnt"] * 32
        root_dir_secs = math.ceil(root_dir_bytes / self.boot_sector["BytsPerSec"])
        
        self.data_start_byte = self.root_dir_start_byte + (root_dir_secs * self.boot_sector["BytsPerSec"])
        self.bytes_per_cluster = self.boot_sector["SecPerClus"] * self.boot_sector["BytsPerSec"]

    def load_fat(self):
        """FAT tablosunu belleğe yükler."""
        fat_size = self.boot_sector["FATSz16"] * self.boot_sector["BytsPerSec"]
        self.image.seek(self.boot_sector["RsvdSecCnt"] * self.boot_sector["BytsPerSec"])
        self.fat_table = self.image.read(fat_size)

    def get_fat_entry(self, cluster_num):
        """FAT12'nin karmaşık 12-bitlik girişini okur."""
        idx = cluster_num * 3 // 2
        two_bytes = struct.unpack('<H', self.fat_table[idx:idx + 2])[0]
        
        if cluster_num % 2 == 0:
            return two_bytes & 0x0FFF
        else:
            return two_bytes >> 4

    def read_file(self, target_name):
        """Root dizinini tarar ve hedef dosyayı okur."""
        self.image.seek(self.root_dir_start_byte)
        root_dir_data = self.image.read(self.boot_sector["RootEntCnt"] * 32)
        
        file_entry = None
        for i in range(0, len(root_dir_data), 32):
            entry = root_dir_data[i:i+32]
            if entry[0] == 0x00: break
            if entry[0] == 0xE5 or entry[11] == 0x0F: continue
            
            name = entry[0:11].decode('ascii').strip()
            if name == target_name:
                file_entry = {
                    "start_cluster": struct.unpack('<H', entry[26:28])[0],
                    "size": struct.unpack('<I', entry[28:32])[0]
                }
                break

        if not file_entry:
            return f"Hata: {target_name} bulunamadı."

        # Küme zincirini takip ederek veriyi oku
        content = b""
        curr = file_entry["start_cluster"]
        while curr < 0xFF8:
            offset = self.data_start_byte + (curr - 2) * self.bytes_per_cluster
            self.image.seek(offset)
            content += self.image.read(self.bytes_per_cluster)
            curr = self.get_fat_entry(curr)
            
        return content[:file_entry["size"]].decode('ascii')

if __name__ == "__main__":
    reader = FAT12Reader("sample.img")
    reader.open_image()
    reader.parse_boot_sector()
    reader.load_fat()
    
    print(f"Sistem: {reader.boot_sector['FilSysType']} | Etiket: {reader.boot_sector['VolLab']}")
    content = reader.read_file("ASSIGN~0TXT")
    print("\n--- ASSIGNMENT.TXT İçeriği ---")
    print(content)
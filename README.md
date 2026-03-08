# FAT12-Project

This project is a Python-based parser for the **FAT12 file system**. It was developed to understand the low-level structure of storage devices, specifically focusing on how data is organized in sectors, clusters, and the File Allocation Table (FAT).

## Features
- **Boot Sector Parsing:** Extracts metadata such as bytes per sector, sectors per cluster, and FAT size using the Python `struct` module.
- **Root Directory Scanning:** Navigates the root directory to locate files using the 8.3 filename standard.
- **Cluster Chain Traversal:** Implements the 12-bit entry logic to follow file chunks across the drive.
- **File Data Extraction:** Reads and displays the content of specific files (e.g., `ASSIGNMENT.TXT`) from a disk image.

## Technical Details
The project handles the specific calculations required for FAT12, such as:
- **Byte Offset:** The position of a cluster on the disk is calculated as:
  
  `Offset = Data_Start_Byte + (cluster_num - 2) * Bytes_Per_Cluster`

- **12-bit FAT Entries:** Since FAT12 uses 1.5 bytes per entry, the index is calculated as 3 * cluster / 2, followed by bit-masking to extract the correct value.

## How to Run
1. Ensure you have a FAT12 disk image named `sample.img` in the project directory.
2. Run the Jupyter Notebook `fat_file_system.ipynb`.

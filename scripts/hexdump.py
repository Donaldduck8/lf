def format_hex(byte):
    return f"{byte:02x}"

def main(filename):
    try:
        with open(filename, 'rb') as file:
            # Read 1024 bytes
            chunk = file.read(1024)

            # Convert to hexadecimal
            hex_chunk = [format_hex(byte) for byte in chunk]

            # Convert to ASCII
            ascii_chunk = [chr(byte) if 32 <= byte < 127 else '.' for byte in chunk]

            # Print hex and ASCII representation
            hex_part = ' '.join(hex_chunk)
            ascii_part = ''.join(ascii_chunk)

            print(f"{hex_part:47}  {ascii_part}")

    except FileNotFoundError:
        print(f"File not found: {filename}")
    except PermissionError:
        print(f"Permission denied: {filename}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python hexdump.py <filename>")
    else:
        filename = sys.argv[1]
        main(filename)

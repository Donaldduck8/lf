import os
import sys
import binascii
import subprocess
import traceback
import keyboard
import pygments
import pygments.lexers
import pygments.formatters
import refinery.lib.meta
# import chardet
from pygments.formatters import TerminalFormatter

HERE = os.path.dirname(os.path.abspath(__file__))

def _write_lineno_better(self, outfile):
    self._lineno += 1
    lineno_s = str(self._lineno).zfill(2)
    outfile.write("\033[95m%s%s \033[34m│ \033[37m" % (self._lineno != 1 and '\n' or '', lineno_s))

TerminalFormatter._write_lineno = _write_lineno_better

def preview_text(path, peek_buf, window_width, window_height, window_x, window_y):
    #detection = chardet.detect(peek_buf)
    #encoding = detection["encoding"]
    with open(path, "r", encoding="utf-8", errors="ignore") as path_f:
        content = "".join([path_f.readline() for x in range(window_height)])
        content = content.replace("\t", "    ")
    
    if len(content) == 0:
        return
    try:
        lexer = pygments.lexers.get_lexer_for_filename(path)
    except:
        lexer = pygments.lexers.get_lexer_for_filename("a.txt")
    formatter = pygments.formatters.get_formatter_by_name("terminal", linenos=True)
    print(pygments.highlight(content, lexer, formatter))
        

def preview_hex_dump(path, buf, window_width, window_height, window_x, window_y):
    address_width = 4
    column_separator = "\033[94m │ \033[97m"
    column_cross = "\033[94m─┼─\033[97m"
    column_separator_width = 3
    column_separator_side_width = int((column_separator_width - 1) / 2)

    remaining_line_width = window_width - (address_width + column_separator_width + column_separator_width)

    # Divide remaining line width between hex and char displays
    hex_width = int(remaining_line_width * 2/3)
    hex_width = hex_width - (hex_width % 12)
    char_width = int(hex_width / 3)

    meta = refinery.lib.meta.metavars(buf)
    magic = str(meta.magic)
    if len(magic) > hex_width:
        magic = magic[:hex_width-4] + "..."
    entropy = 'Entropy: \033[96m{:.2%}\033[0m'.format(meta.entropy).center(char_width)

    magic_buf = ""
    magic_buf += " " * (address_width)
    magic_buf += column_separator
    magic_buf += "\033[93m" + magic.center(hex_width - 1) + "\033[0m"
    magic_buf += column_separator
    magic_buf += entropy

    print(magic_buf)

    # Print header
    header_buf = ""
    header_buf += " " * (address_width)
    header_buf += column_separator

    header_buf += "\033[95m" + " ".join([hex(x)[2:].zfill(2) for x in range(char_width)]).upper()
    header_buf += column_separator

    print(header_buf)

    window_height -= 1

    separator_line_buf = "\033[94m"
    separator_line_buf += "─" * address_width

    separator_line_buf += "─" * column_separator_side_width
    separator_line_buf += "┼"
    separator_line_buf += "─" * column_separator_side_width

    separator_line_buf += "─" * (hex_width - 1)

    separator_line_buf += "─" * column_separator_side_width
    separator_line_buf += "┼"
    separator_line_buf += "─" * column_separator_side_width

    separator_line_buf += "─" * char_width
    separator_line_buf += "\033[97m"

    print(separator_line_buf)
    window_height -= 1

    for line_number in range(window_height):
        line_buf = ""
        buf_offset = char_width * line_number

        if buf_offset > len(buf):
            break

        buf_slice = buf[buf_offset:buf_offset + char_width]

        address_string = "\033[95m" + hex(buf_offset)[2:].zfill(4).upper()
        line_buf += address_string + column_separator

        hex_slice = binascii.hexlify(buf_slice, sep=" ").decode().ljust(hex_width - 1).upper()
        if meta.entropy < 0.4:
            hex_slice = hex_slice.replace("00", "\033[90m00\033[0m")
        line_buf += hex_slice + column_separator

        char_slice = bytearray()
        for val in buf_slice:
            if val < 33 or val > 126:
                char_slice += bytearray("\033[90m.\033[0m".encode())
            else:
                char_slice.append(val)

        char_slice = "".join([chr(x) for x in char_slice])

        line_buf += char_slice

        print(line_buf)

        line_number += 1

if __name__ == "__main__":
    try:
        command = sys.argv[1]
        arguments = sys.argv[2:]
        file_path = arguments[0]
        file_path = file_path.replace("\\", "/")

        arguments = arguments[1:]

        if command == "send-nvim":
            sender_id = arguments[0]
            args = ["lf", "-remote", f'send-others {sender_id} !nvim "{file_path}"']
            subprocess.run(args, shell=True)

        elif command == "alt-down":
            keyboard.press_and_release("alt+down")

        elif command == "preview":
            sys.stdout.reconfigure(encoding="utf-8")
            window_width, window_height, window_x, window_y = [int(x) for x in arguments]

            with open(file_path, "rb") as file_f:
                peek_buf = file_f.read(int(window_width * window_height / 3))

                # Is this a text file or a binary file?
                is_text = True
                for val in peek_buf:
                    if val == 0:
                        is_text = False
                        break

                if is_text:
                    preview_text(file_path, peek_buf, window_width, window_height, window_x, window_y)
                else:
                    preview_hex_dump(file_path, peek_buf, window_width, window_height, window_x, window_y)

    except:
        print(traceback.format_exc())
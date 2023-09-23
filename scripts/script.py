import time
GLOBAL_START = time.time()

import os
import sys

BLACK = "\033[0\;30m"
RED = "\033[0\;31m"
GREEN = "\033[0\;32m"
YELLOW = "\033[0\;33m"
LAVENDER = "\033[0\;34m"
PINK = "\033[0\;35m"
CYAN = "\033[0\;36m"
WHITE = "\033[0\;37m"

BLACK_BRIGHT = "\033[0\;90m"
RED_BRIGHT = "\033[0\;91m"
GREEN_BRIGHT = "\033[0\;92m"
YELLOW_BRIGHT = "\033[0\;93m"
LAVENDER_BRIGHT = "\033[0\;94m"
PINK_BRIGHT = "\033[0\;95m"
CYAN_BRIGHT = "\033[0\;96m"
WHITE_BRIGHT = "\033[0\;97m"

RESET = "\033[0m"

SUCCESS_COLOR = GREEN
FAILURE_COLOR = RED
HIGHLIGHT_COLOR = YELLOW_BRIGHT
HIGHLIGHT_ALT_COLOR = CYAN
LINE_NO_COLOR = PINK_BRIGHT
SEPARATOR_COLOR = LAVENDER_BRIGHT

HERE = os.path.dirname(os.path.abspath(__file__))

def preview_text(path, peek_buf, window_width, window_height, window_x, window_y):
    import pygments
    import pygments.lexers
    import pygments.formatters
    from pygments.formatters import TerminalFormatter

    # Improve line number formatting
    def _write_lineno_better(self, outfile):
        self._lineno += 1
        lineno_s = str(self._lineno).zfill(2)
        lineno_text = "%s%s" % (self._lineno != 1 and "\n" or "", lineno_s)
        outfile.write(f'{LINE_NO_COLOR}{lineno_text} {SEPARATOR_COLOR}│ {RESET}')

    TerminalFormatter._write_lineno = _write_lineno_better

    # Read as many lines as can be displayed
    with open(path, "r", encoding="utf-8", errors="ignore") as path_f:
        content = "".join([path_f.readline() for x in range(window_height)])

        # Replace tabs with 4 spaces for consistent indentation look and feel
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
    start = time.time()
    import refinery.lib.meta

    window_height -= 2

    address_width = 4
    column_separator = f"{SEPARATOR_COLOR} │ {RESET}"
    column_cross = f"─┼─"
    column_separator_width = 3

    remaining_line_width = window_width - (address_width + column_separator_width + column_separator_width)

    # Divide remaining line width between hex and char displays
    hex_width = int(remaining_line_width * 2/3)
    hex_width = hex_width - (hex_width % 16)
    char_width = int(hex_width / 3)

    meta = refinery.lib.meta.metavars(buf)
    magic = str(meta.magic)
    if len(magic) > hex_width:
        magic = magic[:hex_width-4] + "..."

    # Very simple entropy calculation
    import math
    total_bytes = len(buf)
    byte_probs = [max(buf.count(byte) / total_bytes, 0.000000000001) for byte in range(256)]
    entropy = 0.0 + -sum(math.log(p, 2) * p for p in byte_probs) / 8.0
    
    entropy_percentage_string = "{:.2%}".format(entropy)
    entropy = f'Entropy: {HIGHLIGHT_ALT_COLOR}{entropy_percentage_string}{RESET}'.center(char_width)

    magic_buf = ""
    magic_buf += " " * (address_width)
    magic_buf += column_separator
    magic_buf += HIGHLIGHT_COLOR + magic.center(hex_width - 1) + RESET
    magic_buf += column_separator
    magic_buf += entropy

    print(magic_buf)
    window_height -= 1

    # Print header
    header_buf = ""
    header_buf += " " * (address_width)
    header_buf += column_separator

    header_buf += LINE_NO_COLOR + " ".join([hex(x)[2:].zfill(2) for x in range(char_width)]).upper()
    header_buf += column_separator

    print(header_buf)

    window_height -= 1

    separator_line_buf = SEPARATOR_COLOR
    separator_line_buf += "─" * address_width
    separator_line_buf += column_cross
    separator_line_buf += "─" * (hex_width - 1)
    separator_line_buf += column_cross
    separator_line_buf += "─" * char_width
    separator_line_buf += RESET

    print(separator_line_buf)
    window_height -= 1

    for line_number in range(window_height):
        line_buf = ""
        buf_offset = char_width * line_number

        if buf_offset > len(buf):
            break

        buf_slice = buf[buf_offset:buf_offset + char_width]

        address_string = LINE_NO_COLOR + hex(buf_offset)[2:].zfill(4).upper()
        line_buf += address_string + column_separator


        currently_darkened = False
        hex_slice = ""
        for val in buf_slice:
            if val == 0:
                if not currently_darkened:
                    currently_darkened = True
                    hex_slice += BLACK_BRIGHT
            else:
                if currently_darkened:
                    currently_darkened = False
                    hex_slice += RESET
            hex_slice += format(val, "02x") + " "

        hex_slice = hex_slice[:-1]
        line_buf += hex_slice + column_separator

        char_slice = bytearray()
        for val in buf_slice:
            if val < 33 or val > 126:
                char_slice += bytearray(f"{BLACK_BRIGHT}.{RESET}".encode())
            else:
                char_slice.append(val)

        char_slice = "".join([chr(x) for x in char_slice])

        line_buf += char_slice

        print(line_buf)

        line_number += 1

    end = time.time()

def lf_remote(remote_command: str, shell=False):
    import subprocess
    args = ["lf", "-remote", remote_command]
    p = subprocess.run(args, shell=shell)

def handle_command(command, selected_path, extra_arguments):
    if os.path.isdir(selected_path):
        folder_path = selected_path
    else:
        file_path = selected_path
        folder_path = os.path.dirname(file_path)

    if command == "send-nvim":
        sender_id = extra_arguments[0]
        lf_remote(f'send-others {sender_id} $nvim "{selected_path}"')

    elif command == "alt-down":
        import keyboard
        keyboard.press_and_release("alt+down")

    elif command == "preview":
        sys.stdout.reconfigure(encoding="utf-8")
        window_width, window_height, window_x, window_y = [int(x) for x in extra_arguments]

        with open(selected_path, "rb") as file_f:
            peek_buf = file_f.read(int(window_width * window_height / 3))

            # Is this a text file or a binary file?
            is_text = True
            for val in peek_buf:
                if val == 0:
                    is_text = False
                    break

            if is_text:
                preview_text(selected_path, peek_buf, window_width, window_height, window_x, window_y)
            else:
                preview_hex_dump(selected_path, peek_buf, window_width, window_height, window_x, window_y)
    elif command == "create-file":
        new_file_name = input("Enter a file name: ")
        new_file_path = os.path.join(folder_path, new_file_name)

        if os.path.exists(new_file_path):
            lf_remote(f'send echo {FAILURE_COLOR}The requested file {HIGHLIGHT_COLOR}{new_file_name} {FAILURE_COLOR}already exists!{RESET}')
            return

        with open(new_file_path, "wb+") as new_file_f:
            pass

        lf_remote(f'send echo {SUCCESS_COLOR}Created {HIGHLIGHT_COLOR}{new_file_name} {SUCCESS_COLOR}successfully!{RESET}')

    elif command == "create-dir":
        new_folder_name = input("Enter a folder name: ")
        new_folder_path = os.path.join(folder_path, new_folder_name)

        if os.path.exists(new_folder_path):
            lf_remote(f'send echo {FAILURE_COLOR}The requested folder {HIGHLIGHT_COLOR}{new_folder_name} {FAILURE_COLOR}already exists!{RESET}')
            return

        os.makedirs(new_folder_path)

        lf_remote(f'send echo {SUCCESS_COLOR}Created {HIGHLIGHT_COLOR}{new_folder_name} {SUCCESS_COLOR}successfully!{RESET}')

if __name__ == "__main__":
    try:
        command = sys.argv[1]

        selected_path = sys.argv[2]
        selected_path = selected_path.replace("\\", "/")

        extra_arguments = sys.argv[3:]

        handle_command(command, selected_path, extra_arguments)
    except:
        import traceback
        print(traceback.format_exc())
    GLOBAL_END = time.time()

    print(f"Total Python time: {(GLOBAL_END - GLOBAL_START) * 1000}ms")
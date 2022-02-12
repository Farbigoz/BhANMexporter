import os
import sys

sys.path.clear()
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), "Lib"))

import ctypes
import traceback


TRACEBACK_FILE_NAME = "python.traceback.txt"


def main():
    try:
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

        import main
        main.main(*sys.argv)

    except SystemExit as e:
        pass

    except:
        error = "".join(traceback.format_exception(*sys.exc_info()))

        result = ctypes.windll.user32.MessageBoxW(None, error[:400] + "\n" * 2 + "Open log txt file?",
                                                  "Python traceback", 0x04 | 0x10)

        with open(TRACEBACK_FILE_NAME, "w", encoding="UTF-8") as f:
            f.write(error)

        if result == 6:
            os.startfile(TRACEBACK_FILE_NAME)


if __name__ == '__main__':
    main()

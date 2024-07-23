class Logger:
    def __init__(self):
        self._colors = {
            "RED": "\033[31m",
            "GREEN": "\033[32m",
            "YELLOW": "\033[33m",
            "GRAY": "\033[37m",
            "RESET": "\033[0m"
        }
    def info(self, msg):
        print(f"{self._colors.get("GRAY")}[INFO] {msg}{self._colors.get("RESET")}")

    def error(self, msg):
        print(f"{self._colors.get("RED")}[ERROR] {msg}{self._colors.get("RESET")}")

    def warn(self, msg):
        print(f"{self._colors.get("YELLOW")}[WARNING] {msg}{self._colors.get("RESET")}")

    def success(self, msg):
        print(f"{self._colors.get("GREEN")}[SUCCESS] {msg}{self._colors.get("RESET")}")

logger = Logger()

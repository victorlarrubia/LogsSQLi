import re
import csv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
INPUT_FILE = BASE_DIR / "logs" / "access.log"
OUTPUT_FILE = BASE_DIR / "data" / "raw" / "access_log_structured.csv"

LOG_PATTERN = re.compile(
    r'(?P<remote_addr>\S+) - (?P<remote_user>\S+) '
    r'\[(?P<time_local>[^\]]+)\] '
    r'"(?P<request>[^"]*)" '
    r'(?P<status>\d{3}) '
    r'(?P<body_bytes_sent>\d+) '
    r'"(?P<http_referer>[^"]*)" '
    r'"(?P<http_user_agent>[^"]*)" '
    r'rt=(?P<request_time>\S+)'
)

def main():
    total = 0
    converted = 0
    failed = 0

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(INPUT_FILE, "r", encoding="utf-8", errors="replace") as fin, \
         open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as fout:

        fieldnames = [
            "remote_addr",
            "remote_user",
            "time_local",
            "request",
            "status",
            "body_bytes_sent",
            "http_referer",
            "http_user_agent",
            "request_time"
        ]

        writer = csv.DictWriter(fout, fieldnames=fieldnames)
        writer.writeheader()

        for line in fin:
            total += 1
            line = line.rstrip("\n")
            match = LOG_PATTERN.match(line)

            if match:
                writer.writerow(match.groupdict())
                converted += 1
            else:
                failed += 1

    print(f"Input : {INPUT_FILE}")
    print(f"Output: {OUTPUT_FILE}")
    print(f"Total lines     : {total}")
    print(f"Converted lines : {converted}")
    print(f"Failed lines    : {failed}")

if __name__ == "__main__":
    main()

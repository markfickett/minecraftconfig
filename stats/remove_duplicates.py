#!/usr/bin/env python
"""Remove duplicate values in a time-series CSV.

Usage:
  remove_duplicates.py input.csv output.csv
"""

import csv
import sys

if __name__ == '__main__':
  with open(sys.argv[1]) as in_file, open(sys.argv[2], 'w') as out_file:
    reader = csv.reader(in_file)
    writer = csv.writer(out_file)
    prev_written = True
    prev_timestamp = None
    prev_value = None
    for timestamp, value in reader:
      if value != prev_value:
        if not prev_written:
          writer.writerow((prev_timestamp, prev_value))
        writer.writerow((timestamp, value))
        prev_written = True
      else:
        prev_written = False
      prev_timestamp, prev_value = timestamp, value
    if not prev_written:
      writer.writerow((prev_timestamp, prev_value))

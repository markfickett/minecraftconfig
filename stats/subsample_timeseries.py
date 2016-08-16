#!/usr/bin/env python
"""Remove most rows older in the history of a timeseries CSV.

Usage:
  subsample_timeseries.py input.csv output.csv
"""

import csv
import sys

WINDOW_ROWS = 60 * 24
RECENT_ROWS = 60 * 24 * 30  #  Keep full resolution for the last month.
ANALYSIS_VALUE = 'coretemp-isa-0000 Physical id 0'

def SimplifyRows(rows, analysis_index):
  return [rows[-1]]

class RowBuffer(object):
  """Iterator that returns chunks of rows.

  This holds a reserve of RECENT_ROWS rows at all times, and does not return
  them during normal iteration. And, it returns WINDOW_ROWS rows at a time
  during iteration.
  """
  def __init__(self, csv_reader):
    self._csv_reader = csv_reader
    self._row_buffer = []

  def __iter__(self):
    return self

  def next(self):
    while len(self._row_buffer) < RECENT_ROWS:
      self._row_buffer.append(self._csv_reader.next())
    chunk, self._row_buffer = (
        self._row_buffer[:WINDOW_ROWS], self._row_buffer[WINDOW_ROWS:])
    return chunk

  def GetRemainingRows(self):
    return self._row_buffer

if __name__ == '__main__':
  with open(sys.argv[1]) as in_file, open(sys.argv[2], 'w') as out_file:
    reader = csv.reader(in_file)
    writer = csv.writer(out_file)
    headers = reader.next()
    analysis_index = headers.index(ANALYSIS_VALUE)
    writer.writerow(headers)

    buffer = RowBuffer(reader)
    try:
      for row_chunk in buffer:
        for simplified in SimplifyRows(row_chunk, analysis_index):
          writer.writerow(simplified)
      for row in buffer.GetRemainingRows():
        writer.writerow(row)
    except csv.Error, e:
      print e, reader.line_num

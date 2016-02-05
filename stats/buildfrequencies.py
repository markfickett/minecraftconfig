#!/usr/bin/env python
"""Build frequency data from time series data for Minecraft login status.

Usage:
  %s crafters.csv crafters-frequency.csv
"""

import csv
import datetime
import sys


class Pt(object):
  def __init__(self):
    self.counts = []

  @property
  def probability(self):
    if not self.counts:
      return 0
    return sum(filter(bool, self.counts)) / float(len(self.counts))

  @property
  def population(self):
    present = filter(bool, self.counts)
    if not present:
      return 0
    return sum(present) / float(len(present))


def MakeFrequencyContainer():
  days = []
  for _ in xrange(7):
    counts = []
    for _ in xrange(24):
      counts.append(Pt())
    days.append(counts)
  return days


def FillFrequencies(time_series_reader, frequencies, now, max_age_days):
  for row_num, (timestamp_str, count) in enumerate(time_series_reader):
    if timestamp_str is 'Time':
      print 'skipping header:', timestamp_str
      continue
    try:
      timestamp = datetime.datetime.strptime(
          timestamp_str, '%Y-%m-%dT%H:%M:%S.%f')
    except ValueError, e:
      print 'Timestamp error on line %d parsing %r:\n%s' % (
          row_num, timestamp_str, e)
      continue
    if max_age_days and (now - timestamp) > max_age_days:
      continue
    frequencies[timestamp.weekday()][timestamp.hour].counts.append(int(count))


def WriteFrequencies(frequencies_writer, frequencies):
  frequencies_writer.writerow(['day','hour','probability','population'])
  for day, hours in enumerate(frequencies):
    for hour, pt in enumerate(hours):
      if not any(pt.counts):
        continue
      frequencies_writer.writerow([day, hour, pt.probability, pt.population])


if __name__ == '__main__':
  if len(sys.argv) not in (3, 4):
    print __doc__
    sys.exit(1)
  if len(sys.argv) == 4:
    max_age_days = datetime.timedelta(days=int(sys.argv[3]))
  else:
    max_age_days = None

  with open(sys.argv[1], 'r') as time_series_file, \
      open(sys.argv[2], 'w') as frequency_file:
    frequencies = MakeFrequencyContainer()
    FillFrequencies(
        csv.reader(time_series_file),
        frequencies,
        datetime.datetime.utcnow(),
        max_age_days)
    WriteFrequencies(csv.writer(frequency_file), frequencies)

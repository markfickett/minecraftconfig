#!/usr/bin/python
"""Log CPU/disk temperatures to one CSV file, Minecrafter count to another."""

import collections
import csv
import datetime
import logging
import os
import re
import subprocess
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), 'minecraftstatus'))
import mcstatus


HTML_DIR = '/home/minecraft/public_html/'

TEMPERATURE_CSV_PATH = os.path.join(HTML_DIR, 'temperatures.csv')
TEMPERATURE_PATTERN = re.compile('[\+-]?([0-9.]+).+C.*')
TEMPERATURE_GROUP_NUM = 1
SENSORS_LINE_PATTERN = re.compile('([^:]*):([^(]+)(\(.*)')
SENSORS_ITEM_GROUP_NUM = 1
SENSORS_TEMP_GROUP_NUM = 2

MINECRAFT_CSV_PATH = os.path.join(HTML_DIR, 'crafters.csv')


def GetTemperatureData(formatted_now):
  data = collections.OrderedDict()
  data['Time'] = formatted_now
  AddSensorsData(data, GetSensorsOutput())
  AddHddData(data, GetHddOutput())
  return data


def GetDegreesC(temp_str):
  re_match = TEMPERATURE_PATTERN.match(temp_str)
  if not re_match:
    return None
  return float(re_match.group(TEMPERATURE_GROUP_NUM))


def AddSensorsData(data, sensors_output):
  section_name = None
  for raw_line in sensors_output.split('\n'):
    line = raw_line.strip()
    if not line:
      section_name = None
      continue
    if ':' not in line:
      section_name = line
      continue
    re_match = SENSORS_LINE_PATTERN.match(line)
    if not re_match:
      continue
    item_name = re_match.group(SENSORS_ITEM_GROUP_NUM)
    if 'TIN' in item_name:
      continue
    temp_str = re_match.group(SENSORS_TEMP_GROUP_NUM)
    t = GetDegreesC(temp_str.strip())
    if t is not None:
      data['%s %s' % (section_name, item_name)] = t


def AddHddData(data, hdd_output):
  for drive_info_raw in hdd_output.split('||'):
    drive_info = drive_info_raw.strip('|')
    device_name, unused_long_name, temp_str, unused_c = drive_info.split('|')
    data[device_name] = int(temp_str)


def GetSensorsOutput():
  return subprocess.check_output(['sensors'])


def GetHddOutput():
  # If this fails, run as root:
  # hddtemp -d /dev/sd[abc]
  return subprocess.check_output(['nc', 'localhost', '7634'])


def GetMinecraftData(server, formatted_now):
  data = collections.OrderedDict()
  data['Time'] = formatted_now
  data['Players Online'] = server.num_players_online
  return data

def UpdateCsv(path, ordered_dict):
  write_headers = not os.path.isfile(path)
  with open(path, 'a') as raw_file:
    csv_writer = csv.writer(raw_file)
    if write_headers:
      csv_writer.writerow(ordered_dict.keys())
    csv_writer.writerow(ordered_dict.values())


if __name__ == '__main__':
  server = mcstatus.McServer('localhost')
  server.Update()
  now = datetime.datetime.utcnow().isoformat()
  try:
    UpdateCsv(TEMPERATURE_CSV_PATH, GetTemperatureData(now))
  except subprocess.CalledProcessError:
    logging.error(
        'Error getting HD temps. Run hddtemp -d /dev/sd[abc] ?',
        exc_info=True)
  UpdateCsv(MINECRAFT_CSV_PATH, GetMinecraftData(server, now))

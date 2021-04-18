import csv
import json
import os
import re


def get_avg_power_and_total_energy(path):
	pattern = re.compile("Power")
	desired_lines = []
	for i, line in enumerate(open(path)):
		for match in re.finditer(pattern, line):
			desired_lines.append(line)
	return float(desired_lines[2].split(",")[2]), float(desired_lines[2].split(",")[3])


if __name__ == "__main__":
	path_test = '/home/ridi/Desktop/Research_VVC_HM/SoCWatchOutput.csv'
	avg_power, total_energy = get_avg_power_and_total_energy(path_test)
	print(avg_power, total_energy)

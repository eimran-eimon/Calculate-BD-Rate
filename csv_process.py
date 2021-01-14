import pandas as pd
import glob
import csv
import os

path = '/home/ridi/Desktop/Research_VVC_HM/results/hm/low_delay.cfg/CLASS_A/'
list_of_csv_file = os.listdir(path)
print(list_of_csv_file)
for csv in list_of_csv_file:
	with open(f"{path}{csv}") as f:
		csv_list = [[val.strip() for val in r.split("\t")] for r in f.readlines()]

		(_, *header), *data = csv_list
		csv_dict = {}
		for row in data:
			key, *values = row
			if key not in csv_dict:
				csv_dict[key] = values[0]
			elif key in csv_dict:
				print(f"{key} = {float(csv_dict[key]) + float(values[0])}")

	# print(csv_dict)

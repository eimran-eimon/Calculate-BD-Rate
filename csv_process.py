import csv


def write_cpu_consuming_classes(path, total_cpu_time):
	print(f"Path: {path}")
	with open(f"{path}") as f:

		csv_list = [[val.strip() for val in r.split("\t")] for r in f.readlines()]

		(_, *header), *data = csv_list
		csv_dict = {}
		for row in data:
			key, *values = row
			class_name = key.split("::")
			if len(class_name) > 1:
				if class_name[1] not in csv_dict:
					csv_dict[class_name[1]] = float(values[1])
				elif class_name[1] in csv_dict:
					csv_dict[class_name[1]] = float(csv_dict[class_name[1]]) + float(values[1])

	for key in csv_dict:
		csv_dict[key] = round((csv_dict[key] / total_cpu_time) * 100, 3)

	csv_dict = {k: v for k, v in sorted(csv_dict.items(), key=lambda item: item[1], reverse=True)}
	file_name = path.rpartition("/")[-1].split(".")[:-1]
	print(f'File: {"_".join(file_name)}_by_class.csv')
	with open(f'{path.rpartition("/")[0]}/{"_".join(file_name)}_by_class.csv', 'w') as f:
		w = csv.writer(f)
		w.writerow(["Class", "CPU Time (%)"])
		for key, value in csv_dict.items():
			w.writerow([key, value])

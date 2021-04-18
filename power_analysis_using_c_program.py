import os
import re
import math
import numpy as np

prefix_path = "./rapl"
app_name = "AppPowerMeter"


def write_sh_file(cmd, sudo_cmd):
	os.system(f"{sudo_cmd} rm {prefix_path}/cmd.sh")
	f = open(f"{prefix_path}/cmd.sh", "w")
	f.write(f"#!/bin/sh\n{cmd}")
	f.close()


def chmod_sh_file(cmd, sudo_cmd):
	write_sh_file(cmd, sudo_cmd)
	os.system(f"chmod 755 {prefix_path}/cmd.sh")


def run_power_analysis(sudo_cmd, cmd):
	write_sh_file(cmd, sudo_cmd)
	chmod_sh_file(cmd, sudo_cmd)
	os.system(f"{sudo_cmd} {prefix_path}/AppPowerMeter {prefix_path}/cmd.sh > tmp.txt")
	pattern = re.compile("\tAverage Power")

	desired_lines = []

	for i, tmp_line in enumerate(open('tmp.txt')):
		for match in re.finditer(pattern, tmp_line):
			desired_lines.append(tmp_line)

	if desired_lines:
		summary_line = str(desired_lines[0])
		summary_data = summary_line.split(":")
		# print(f"Summary: {summary_data}")
		return summary_data[1].split(" ")[0]


def run_samples(avg_power_array, cmd, no_of_samples, sudo_cmd):
	for i in range(1, no_of_samples + 1):
		avg_power = run_power_analysis(sudo_cmd, cmd)
		avg_power_array = np.append(avg_power_array, float(avg_power))
	return avg_power_array


def check_confidence_interval(avg_power_array, no_of_samples):
	t_alpha = 2.845 # 99% confidence interval
	beta = 0.2
	mean, std = np.mean(avg_power_array), np.std(avg_power_array)
	err_tolerance = 2 * ((std / math.sqrt(no_of_samples)) * t_alpha)
	print(f"Confidence Interval: {err_tolerance}, Beta x Mean = {beta * mean}")
	confidence_interval_bool = 2 * ((std / math.sqrt(no_of_samples)) * t_alpha) < (beta * mean)
	return confidence_interval_bool


def get_avg_power_consumption(sudo_cmd, cmd, no_of_samples):
	avg_power = -math.inf

	while avg_power < 0:
		avg_power_array = np.array([])
		avg_power_array = run_samples(avg_power_array, cmd, no_of_samples, sudo_cmd)
		if check_confidence_interval(avg_power_array, no_of_samples):
			avg_power = avg_power_array.mean()
			break

	return avg_power


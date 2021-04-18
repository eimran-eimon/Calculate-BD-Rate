import os
import re
import math
import numpy as np

prefix_path = "./socwatch"
app_name = "socwatch"


def write_sh_file(cmd, sudo_cmd):
	if os.path.exists(f"{prefix_path}/cmd.sh"):
		os.system(f"{sudo_cmd} rm {prefix_path}/cmd.sh")
	f = open(f"{prefix_path}/cmd.sh", "w")
	f.write(f"#!/bin/sh\n{cmd}")
	f.close()


def chmod_sh_file(cmd, sudo_cmd):
	write_sh_file(cmd, sudo_cmd)
	os.system(f"{sudo_cmd} chmod 755 {prefix_path}/cmd.sh")


def run_power_analysis(sudo_cmd, cmd):
	chmod_sh_file(cmd, sudo_cmd)
	os.system(
		f"{sudo_cmd} {prefix_path}/{app_name} --feature power --result sum --program {prefix_path}/cmd.sh > tmp.txt")


def get_avg_power_and_total_energy(sudo_cmd, cmd, path="./SoCWatchOutput.csv"):
	if os.path.exists(path):
		os.system(f"{sudo_cmd} rm {path}")
		
	run_power_analysis(sudo_cmd, cmd)
	
	pattern = re.compile("Power")
	desired_lines = []
	for i, line in enumerate(open(path)):
		for match in re.finditer(pattern, line):
			desired_lines.append(line)
	return float(desired_lines[2].split(",")[2]), float(desired_lines[2].split(",")[3])


if __name__ == "__main__":
	sudo_cmd_m = 'echo 555555 | sudo -S'
	print(get_avg_power_and_total_energy(sudo_cmd_m, 'ls'))

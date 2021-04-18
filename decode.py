import os
import re
import csv
import weasyprint
import power_analysis
import csv_process

analyzing_types = {'hotspots', 'memory-consumption', 'performance-snapshot', 'memory-access', 'uarch-exploration'}
# analyzing_types = {'hotspots'}
data_fields = ['Seq Name', 'Codec Name', 'Config Name', 'Bitrate (kbps)', 'CPU Time', 'Power Consumption (in W)']
no_of_samples = 20


def start(codec_path, sudo_cmd, vtune_cmd, results_path):
	lines = [line.rstrip() for line in open("bin_file_directories.txt")]

	data_filename = f"./{results_path}/decoders_summary.csv"

	with open(data_filename, 'w', newline='', encoding='utf-8') as csv_file:
		# creating a csv writer object
		csv_writer = csv.writer(csv_file)
		csv_writer.writerow(data_fields)

		for line in lines:
			bin_info = line.split("/")
			decoder_path = f"{codec_path}/{bin_info[2]}/decoder/"
			decoder = os.listdir(decoder_path)[0]

			for analyzing_type in analyzing_types:
				cmd = f"{sudo_cmd} {vtune_cmd} " \
					  f"-collect {analyzing_type} -target-duration-type=veryshort " \
					  f"{decoder_path}{decoder} " \
					  f"-b {line.split('*')[0]}.bin"

				print("--------------------------")
				print(cmd)
				print("--------------------------")

				os.system(f'{cmd} > tmp.txt')

				if analyzing_type == 'hotspots':

					pattern = re.compile(" {4}CPU Time:")

					desired_lines = []

					for i, tmp_line in enumerate(open('tmp.txt')):
						for match in re.finditer(pattern, tmp_line):
							# print('Found on line %s: %s' % (i + 1, match.group()))
							desired_lines.append(tmp_line)
					if desired_lines:
						summary_line = str(desired_lines[0])
						summary_data = summary_line.split()
					else:
						continue

					print(f"CPU time: {summary_data[-1]}")
					report_cmd = f' {sudo_cmd} {vtune_cmd} -report hotspots -r ./r000hs/ -format=csv'
					remove_vtune_result_file = f'{sudo_cmd} rm -r r0*'

					result_dir = f"./{results_path}/{bin_info[2]}/decoder/{bin_info[3]}/{bin_info[4]}/{analyzing_type}/"
					if not os.path.exists(result_dir):
						os.makedirs(result_dir)

					os.system(f'{report_cmd} >> {result_dir}/{bin_info[-1].split("*")[0]}.csv')
					os.system(remove_vtune_result_file)

					only_dec_cmd = f"{decoder_path}{decoder} " \
								   f" -b {line.split('*')[0]}.bin"
					decoding_power = power_analysis.get_avg_power_and_total_energy(sudo_cmd, only_dec_cmd)

					print(f"Decoding Power: {decoding_power}")
					csv_writer.writerows([[line.split("/")[-1].split("*")[0].split("_")[:-1], bin_info[2], bin_info[3],
										line.split('*')[1], summary_data[-1],
										round((decoding_power), 5)]])
					csv_process.write_cpu_consuming_classes(f"{result_dir}/{bin_info[-1].split('*')[0]}.csv", float(summary_data[-1][:-1]))

				elif analyzing_type == 'memory-consumption':
					report_cmd = f' {sudo_cmd} {vtune_cmd} -report hotspots -r ./r000mc/ -format=csv'
					remove_vtune_result_file = f'{sudo_cmd} rm -r r0*'

					result_dir = f"./{results_path}/{bin_info[2]}/decoder/{bin_info[3]}/{bin_info[4]}/{analyzing_type}/"
					if not os.path.exists(result_dir):
						os.makedirs(result_dir)

					os.system(f'{report_cmd} >> {result_dir}/{bin_info[-1].split("*")[0]}.csv')
					os.system(remove_vtune_result_file)

				else:
					if analyzing_type == 'performance-snapshot':
						report_cmd = f' {sudo_cmd} {vtune_cmd} -report summary -r ./r000ps/ -format=html'

					elif analyzing_type == 'memory-access':
						report_cmd = f' {sudo_cmd} {vtune_cmd} -report summary -r ./r000macc/ -format=html'

					elif analyzing_type == 'uarch-exploration':
						report_cmd = f' {sudo_cmd} {vtune_cmd} -report summary -r ./r000ue/ -format=html'

					result_dir = f"./{results_path}/{bin_info[2]}/decoder/{bin_info[3]}/{bin_info[4]}/{analyzing_type}/"
					if not os.path.exists(result_dir):
						os.makedirs(result_dir)

					os.system(f'{report_cmd} >> {result_dir}/{bin_info[-1].split("*")[0]}.html')
					remove_vtune_result_file = f'{sudo_cmd} rm -r r0*'
					os.system(remove_vtune_result_file)
					pdf = weasyprint.HTML(f"{result_dir}/{bin_info[-1].split('*')[0]}.html").write_pdf()
					open(f"{result_dir}/{bin_info[-1].split('*')[0]}.pdf", "wb").write(pdf)


if __name__ == "__main__":
	codec_path_m = './codecs'
	vtune_cmd_m = '/opt/intel/oneapi/vtune/2021.1.1/bin64/vtune'
	sudo_cmd_m = 'echo 555555 | sudo -S'
	results_path_m = f"results_2021_02_10_10_23_46"
	start(codec_path_m, sudo_cmd_m, vtune_cmd_m, results_path_m)

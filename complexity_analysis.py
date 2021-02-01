import csv
import os
import re
import matplotlib
import decode
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
import weasyprint

matplotlib.rcParams.update({'font.size': 6})

frames_to_encode = 2
vtune_cmd = '/opt/intel/oneapi/vtune/2021.1.1/bin64/vtune'
sudo_cmd = 'echo 555555 | sudo -S'
# qps = [22, 27, 32, 37]
qps = [37]
codec_path = './codecs'
config_path = './configs'
sequences_path = './sequences'
results_path = f"./results_{datetime.now().strftime('%Y_%m_%d_%H_%M_%S')}"
# analyzing_types = {'hotspots', 'memory-consumption', 'performance-snapshot', 'memory-access', 'uarch-exploration'}
analyzing_types = {'hotspots'}
rec_yuv_directory = './rec_yuv'
bin_directory = './bin'

data_fields = ['Seq Name', 'Codec Name', 'Config Name', 'QP', 'Bitrate', 'Y-PSNR', 'CPU Time', 'Encoding_FPS/Frame_Rate']

os.system(f'{sudo_cmd} rm -r r0*')
os.system(f'{sudo_cmd} rm -r {bin_directory}')
os.system(f'{sudo_cmd} rm -r {rec_yuv_directory}')

bin_file_directories = open("bin_file_directories.txt", "w")

if not os.path.exists(codec_path):
	print("Codecs not found!")
if not os.path.exists(config_path):
	print("Configs not found!")
if not os.path.exists(sequences_path):
	print("Configs not found!")

if not os.path.exists(rec_yuv_directory):
	os.makedirs(rec_yuv_directory)
if not os.path.exists(bin_directory):
	os.makedirs(bin_directory)
if not os.path.exists(results_path):
	os.makedirs(results_path)

list_of_codecs = os.listdir(codec_path)
list_of_class_sequences = os.listdir(sequences_path)

data_filename = f"{results_path}/encoder_summary.csv"

with open(data_filename, 'w', newline='', encoding='utf-8') as csv_file:
	rate_data = {}
	psnr_data = {}
	# creating a csv writer object
	csv_writer = csv.writer(csv_file)
	csv_writer.writerow(data_fields)
	for codec in list_of_codecs:  # list of provided codecs
		enc_dec_path = f"{codec_path}/{codec}/"

		for enc_dec in os.listdir(enc_dec_path):  # encoder and decoder path
			list_of_enc_dec = os.listdir(f"{enc_dec_path}/{enc_dec}/")
			if len(list_of_enc_dec) != 1:
				print("Only one encoder or decoder should be provided for a codec!")
				break

			if enc_dec == "decoder":
				continue

			# summary_file_path = f"./{results_path}/{codec}/{enc_dec}"
			# if not os.path.exists(summary_file_path):
			# 	os.makedirs(summary_file_path)

			list_of_config = os.listdir(f"{config_path}/{codec}")
			for config in list_of_config:
				for cls in list_of_class_sequences:
					list_of_sequences = os.listdir(f"{sequences_path}/{cls}/")

					for seq in list_of_sequences:

						rate_seq = np.array([])
						psnr_seq = np.array([])

						width_height = seq.split("_")[1].split("x")
						width = width_height[0]
						height = width_height[1]

						if enc_dec == "encoder":
							rate = np.array([])
							psnr = np.array([])

							for qp in qps:
								for analyzing_type in analyzing_types:
									bin_dir_to_store = f"{bin_directory}/{codec}/{config}/{cls}/"
									rec_yuv_dir_to_store = f"{rec_yuv_directory}/{codec}/{config}/{cls}/"

									if not os.path.exists(bin_dir_to_store):
										os.makedirs(bin_dir_to_store)
									if not os.path.exists(rec_yuv_dir_to_store):
										os.makedirs(rec_yuv_dir_to_store)

									cmd = f'{sudo_cmd} {vtune_cmd} -collect {analyzing_type} ' \
										f'{codec_path}/{codec}/{enc_dec}/{list_of_enc_dec[0]} ' \
										f'-c {config_path}/{codec}/{config} ' \
										f'-i {sequences_path}/{cls}/{seq} ' \
										f'-wdt {width} -hgt {height} ' \
										f'-b {bin_dir_to_store}{seq.split(".")[0] + "_QP_" + str(qp) + "_" + codec}.bin ' \
										f'-o {rec_yuv_dir_to_store}{seq.split(".")[0] + "_QP_" + str(qp) + "_" + codec}.yuv ' \
										f'-fr {int(seq.split("_")[2].split(".")[0])} ' \
										f'-fs 0 -f {frames_to_encode} -q {qp} '

									print("--------------------------")
									print(cmd)
									print("--------------------------")

									os.system(f'{cmd} > tmp.txt')

									if analyzing_type == 'hotspots':

										text = open('tmp.txt', 'r').read()
										pattern = re.compile(" {4}CPU Time:")

										desired_lines = []

										for i, line in enumerate(open('tmp.txt')):
											for match in re.finditer(pattern, line):
												# print('Found on line %s: %s' % (i + 1, match.group()))
												desired_lines.append(line)

										summary_line = str(desired_lines[0])
										summary_data = summary_line.split()
										cpu_time = summary_data[-1]

										pattern = re.compile("[\t]")
										desired_lines.clear()

										for i, line in enumerate(open('tmp.txt')):
											for match in re.finditer(re.compile("[\t]"), line):
												# print('Found on line %s: %s' % (i + 1, match.group()))
												desired_lines.append(line)

										if desired_lines:
											summary_line = str(desired_lines[1])
											summary_data = summary_line.split()
											bitrate = summary_data[2]
											y_psnr = summary_data[3]
										else:
											continue

										report_cmd = f' {sudo_cmd} {vtune_cmd} -report hotspots -r ./r000hs/ -format=csv'
										remove_vtune_result_file = f'{sudo_cmd} rm -r r0*'

										result_dir = f"./{results_path}/{codec}/{enc_dec}/{config}/{cls}/{analyzing_type}/"
										if not os.path.exists(result_dir):
											os.makedirs(result_dir)

										os.system(f'{report_cmd} >> {result_dir}/{seq}_qp_{qp}.tsv')
										os.system(remove_vtune_result_file)

										bin_file_directories.write(
											f'{bin_dir_to_store}{seq.split(".")[0] + "_QP_" + str(qp) + "_" + codec + "*" + bitrate}\n')

										rate = np.append(rate, float(bitrate))
										psnr = np.append(psnr, float(y_psnr))

										real_time_indicator = (frames_to_encode/float(cpu_time[:-1])) / int(seq.split("_")[2].split(".")[0])

										csv_writer.writerows([[seq, codec, config, qp, bitrate, y_psnr, cpu_time, round(real_time_indicator, 3)]])

									elif analyzing_type == 'memory-consumption':
										report_cmd = f' {sudo_cmd} {vtune_cmd} -report hotspots -r ./r000mc/ -format=csv'
										remove_vtune_result_file = f'{sudo_cmd} rm -r r0*'

										result_dir = f"./{results_path}/{codec}/{enc_dec}/{config}/{cls}/{analyzing_type}/"
										if not os.path.exists(result_dir):
											os.makedirs(result_dir)

										os.system(f'{report_cmd} >> {result_dir}/{seq}_qp_{qp}.tsv')
										os.system(remove_vtune_result_file)
									else:
										if analyzing_type == 'performance-snapshot':
											report_cmd = f' {sudo_cmd} {vtune_cmd} -report summary -r ./r000ps/ -format=html'

										elif analyzing_type == 'memory-access':
											report_cmd = f' {sudo_cmd} {vtune_cmd} -report summary -r ./r000macc/ -format=html'

										elif analyzing_type == 'uarch-exploration':
											report_cmd = f' {sudo_cmd} {vtune_cmd} -report summary -r ./r000ue/ -format=html'

										result_dir = f"./{results_path}/{codec}/{enc_dec}/{config}/{cls}/{analyzing_type}"
										if not os.path.exists(result_dir):
											os.makedirs(result_dir)

										os.system(f'{report_cmd} >> {result_dir}/{seq}_qp_{qp}.html')
										remove_vtune_result_file = f'{sudo_cmd} rm -r r0*'
										os.system(remove_vtune_result_file)
										pdf = weasyprint.HTML(f"{result_dir}/{seq}_qp_{qp}.html").write_pdf()
										open(f"{result_dir}/{seq}_qp_{qp}.pdf", "wb").write(pdf)

							# RD-Plot
							f = plt.figure()
							plt.plot([], [], ' ', label=f"{codec}")
							plt.plot(rate, psnr, label=f"{config}", marker="o", linewidth=0.6, markersize=2)

							plt.title(f"{seq}")
							plt.xlabel('Bitrate')
							plt.ylabel('PSNR')
							plt.legend(loc="best")
							plt.grid(True)

							plot_dir = f"./{results_path}/{codec}/{enc_dec}/{config}/{cls}/"
							f.savefig(f"{plot_dir + codec + '_qp'}.pdf", bbox_inches='tight')

							rate_data[f"{seq + '|' + cls + '|' + config + '|' + codec}"] = rate
							psnr_data[f"{seq + '|' + cls + '|' + config + '|' + codec}"] = psnr

				f_s = plt.figure()
				plt.plot([], [], ' ', label=f"{codec}")

				for key in rate_data:
					if key.split('|')[2] == config:
						plt.plot(rate_data[key], psnr_data[key], label=f"{key.split('|')[0].split('_')[0], key.split('|')[1]}", marker="o", linewidth=0.6, markersize=2)

				plt.title(f"{config}")
				plt.xlabel('Bitrate')
				plt.ylabel('PSNR')
				plt.legend(loc="best")
				plt.grid(True)

				plot_dir_s = f"./{results_path}/{codec}/{enc_dec}/{config}/"
				f_s.savefig(f"{plot_dir_s + config + '_' + codec}.pdf", bbox_inches='tight')

			for seq_class in list_of_class_sequences:
				f_c = plt.figure()

				for key in rate_data:
					if key.split('|')[3] == codec:
						if key.split('|')[1] == seq_class:
							plt.plot(rate_data[key], psnr_data[key],label=f"{key.split('|')[0].split('_')[0], key.split('|')[2]}", marker="o", linewidth=0.6, markersize=2)

				plt.title(f"{codec} - ({seq_class})")
				plt.xlabel('Bitrate')
				plt.ylabel('PSNR')
				plt.legend(loc="best")
				plt.grid(True)

				plot_dir_c = f"./{results_path}/{codec}/{enc_dec}/"
				f_c.savefig(f"{plot_dir_c + codec +'_'+ seq_class}.pdf", bbox_inches='tight')

bin_file_directories.close()
decode.start(codec_path, sudo_cmd, vtune_cmd, results_path)

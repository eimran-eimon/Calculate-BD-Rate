import os
import re
import csv
from datetime import datetime
import numpy as np
import bjontegaard_metric
import matplotlib.pyplot as plt

frames_to_encode = 2

data_fields = ['Seq Name', 'cfg', 'Codec Name', 'QP', 'Bitrate', 'PSNR']
csv_directory = "stored_csv_files"
rec_yuv_directory = './rec_yuv/'
bin_directory = './bin/'
stored_plots = './plots/'

if not os.path.exists(csv_directory):
	os.makedirs(csv_directory)
if not os.path.exists(rec_yuv_directory):
	os.makedirs(rec_yuv_directory)
if not os.path.exists(bin_directory):
	os.makedirs(bin_directory)
if not os.path.exists(stored_plots):
	os.makedirs(stored_plots)

# name of the csv file
data_filename = f"./{csv_directory}/data_{datetime.now().strftime('%Y_%m_%d_%H_%M_%S')}.csv"

codecs_path = ['./hm/TAppEncoderStatic ', './vtm/EncoderAppStatic ']
qps = [22, 27, 32, 37]

list_of_sequences = os.listdir('./sequences/')

with open(data_filename, 'w', newline='', encoding='utf-8') as csv_file:
	# creating a csv writer object
	csv_writer = csv.writer(csv_file)
	csv_writer.writerow(data_fields)

	for sequence in list_of_sequences:

		width_height = sequence.split("_")[1].split("x")
		width = width_height[0]
		height = width_height[1]

		list_of_configs = os.listdir('./configs/')

		for config_dir in list_of_configs:

			config_files = os.listdir(f'./configs/{config_dir}/')

			R1 = np.array([])
			PSNR1 = np.array([])
			R2 = np.array([])
			PSNR2 = np.array([])

			for codec_path in codecs_path:
				codec_name = codec_path.split("/")[1]

				cfg = None
				for config_file in config_files:
					if config_file.endswith(f"{codec_name}.cfg"):
						cfg = config_file
						break

				for qp in qps:
					encode_cmd_template = f'{codec_path} ' \
								f'-c ./configs/{config_dir}/{cfg} ' \
								f'-i ./sequences/{sequence} ' \
								f'-wdt {width} -hgt {height} ' \
								f'-b {bin_directory}{sequence.split(".")[0] + "_QP_" + str(qp) + "_" + codec_name}.bin ' \
								f'-o {rec_yuv_directory}{sequence.split(".")[0] + "_QP_" + str(qp) + "_" + codec_name}.yuv ' \
								f'-fr {int(sequence.split("_")[2].split(".")[0])} ' \
								f'-fs 0 -f {frames_to_encode} -q {qp} '

					print(encode_cmd_template)
					os.system(f'{encode_cmd_template} > tmp.txt')
					text = open('tmp.txt', 'r').read()
					pattern = re.compile("[\t]")

					desired_lines = []

					for i, line in enumerate(open('tmp.txt')):
						for match in re.finditer(pattern, line):
							# print('Found on line %s: %s' % (i + 1, match.group()))
							desired_lines.append(line)

					summary_line = str(desired_lines[1])
					summary_data = summary_line.split()
					bitrate = summary_data[2]
					y_psnr = summary_data[3]
					csv_writer.writerows([[sequence, cfg, codec_name, qp, bitrate, y_psnr]])

					if codec_name == 'hm':
						R1 = np.append(R1, float(bitrate))
						PSNR1 = np.append(PSNR1, float(y_psnr))
					if codec_name == 'vtm':
						R2 = np.append(R2, float(bitrate))
						PSNR2 = np.append(PSNR2, float(y_psnr))

					print(f"Path= {codec_path}, Seq={sequence}, config={cfg}, QP= {qp}, {summary_line.split()}")

			bd_psnr = bjontegaard_metric.BD_PSNR(R1, PSNR1, R2, PSNR2)
			bd_rate = bjontegaard_metric.BD_RATE(R1, PSNR1, R2, PSNR2)

			f = plt.figure()

			plt.plot([], [], ' ', label=f"BD-PSNR: {round(bd_psnr, 2)}")
			plt.plot([], [], ' ', label=f"BD-RATE: {round(bd_rate, 2)}%")

			plt.plot(R1, PSNR1, label="HM-16.20", marker="o")
			plt.plot(R2, PSNR2, label="VTM-8", marker="o")

			plt.title(f"{sequence}")
			plt.xlabel('Bitrate')
			plt.ylabel('PSNR')
			plt.legend(loc="upper left")

			f.savefig(f"{stored_plots + sequence.split('.')[0] + '_' + config_dir}.pdf", bbox_inches='tight')

	csv_file.close()

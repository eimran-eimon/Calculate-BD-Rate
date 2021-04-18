import os
from random import randint
from pylatex import Document, LongTabu, Tabu, Center, Command, Section, Subsection, NewPage, Table, Subsubsection
from pylatex.utils import bold, NoEscape, italic
import csv
import math
import html_to_dict

codecs_parts = ['encoder', 'decoder']
seq_class_names = ['CLASS_A', 'CLASS_B', 'CLASS_C']


def split_csv_to_pdf_table(doc, data_list, caption_1, caption_2, split_index, no_of_rows=math.inf,
                           empty_row_after=math.inf):
	first_list = []
	second_list = []
	for i, row in enumerate(data_list):
		l1 = list(row[0:split_index])
		if i == 0:
			l1.insert(0, 'Combination No.')
		else:
			l1.insert(0, i)
		first_list.append(l1)
		
		l2 = list(row[split_index:])
		if i == 0:
			l2.insert(0, 'Combination No.')
		else:
			l2.insert(0, i)
		second_list.append(l2)
	
	csv_to_pdf_table(doc, first_list, caption_1, no_of_rows, empty_row_after)
	csv_to_pdf_table(doc, second_list, caption_2, no_of_rows, empty_row_after)


def split_list(data_list, start, end):
	splitted_list = []
	for i, row in enumerate(data_list):
		l1 = list(row[start:end])
		splitted_list.append(l1)
	return splitted_list


def csv_to_pdf_table(doc, data_list, caption, no_of_rows=math.inf, empty_row_after=math.inf):
	if data_list is None or not len(data_list) > 0:
		return
	c = 6 if len(data_list[0]) >= 6 else len(data_list[0])
	fmt = "|"
	for i in range(c):
		fmt = fmt + " X[l] |"
	# print(c)
	row_printed = 0
	with doc.create(LongTabu(fmt)) as data_table:
		doc.append(NoEscape(r'\caption{'))
		doc.append(caption)
		doc.append(NoEscape('}'))
		data_table.add_hline()
		data_table.add_empty_row()
		data_table.add_row(data_list[0][0:c], mapper=[bold])
		data_table.add_empty_row()
		data_table.add_hline()
		data_table.end_table_header()
		data_list.pop(0)
		for i, row in enumerate(data_list):
			if i >= no_of_rows:
				break
			if i > empty_row_after - 1 and i % empty_row_after == 0:
				data_table.add_empty_row()
				data_table.add_hline()
			data_table.add_row(row[0:c])
			data_table.add_hline()
			row_printed = row_printed + 1


def dict_to_pdf_table(doc, caption, selected_metrics, metrics_list, no_of_rows=math.inf,
                      empty_row_after=math.inf):
	fmt = "|"
	for i in range(len(selected_metrics)):
		fmt = fmt + " X[l] |"
	# print(fmt)
	with doc.create(LongTabu(fmt)) as data_table:
		doc.append(NoEscape(r'\caption{'))
		doc.append(caption)
		doc.append(NoEscape('}'))
		data_table.add_hline()
		data_table.add_empty_row()
		data_table.add_row(selected_metrics, mapper=[bold])
		data_table.add_empty_row()
		data_table.add_hline()
		data_table.end_table_header()
		
		for i, row in enumerate(metrics_list):
			if i >= no_of_rows:
				break
			if i > empty_row_after - 1 and i % empty_row_after == 0:
				data_table.add_empty_row()
				data_table.add_hline()
			data_table.add_row(row)
			data_table.add_hline()


def csv_to_list(url, delimiter=","):
	if not os.path.exists(url):
		print(f'Not Found: {url}')
		return
	with open(url) as csv_file:
		reader = csv.reader(csv_file, delimiter=delimiter)
		rows = list(reader)
	return rows


def sort_sub_list(sub_li, column_idx):
	# reverse = None (Sorts in Ascending order)
	# key is set to sort using second element of
	# sublist lambda has been used
	return sorted(sub_li, key=lambda x: x[column_idx], reverse=True)


def generate_pdf(result_path, analyzing_types):
	geometry_options = {
		"landscape": True,
		"margin": "0.5in",
		"headheight": "20pt",
		"headsep": "10pt",
		"includeheadfoot": True
	}
	
	doc = Document(page_numbers=True, geometry_options=geometry_options)
	with open('before_doc_tag.tex') as file:
		before_doc_tex = file.read()
	doc.preamble.append(NoEscape(before_doc_tex))
	doc.preamble.append(NoEscape(r'\usepackage{fancyhdr}'))
	doc.preamble.append(NoEscape(r'\renewcommand{\headrulewidth}{0pt}'))
	
	doc.preamble.append(Command('author', 'Md Eimran Hossain Eimon\n mdeimranhossaineimon@gmail.com'))
	
	with open('after_doc_tag.tex') as file:
		after_doc_tex = file.read()
	doc.append(NoEscape(after_doc_tex))
	doc.append(NoEscape(r'\tableofcontents'))
	doc.append(NoEscape(r'\pagestyle{fancy}'))
	doc.append(NoEscape(r'\fancyhf{}'))
	doc.append(NoEscape(r'\fancyhead[L]{\rightmark}'))
	doc.append(NoEscape(r'\fancyhead[R]{\thepage}'))
	
	doc.append(NewPage())
	
	# summary section
	with doc.create(Section('Analysis Summary')):
		with doc.create(Subsection('Encoding Summary')):
			url = result_path + '/encoder_summary.csv'
			split_csv_to_pdf_table(doc, csv_to_list(url), "Encoding Combination Used", "Encoding Results", 4,
			                       empty_row_after=4)
		doc.append(NewPage())
		with doc.create(Subsection('Decoding Summary')):
			url = result_path + '/decoders_summary.csv'
			split_csv_to_pdf_table(doc, csv_to_list(url), "Decoding Combination Used", "Decoding Results", 3,
			                       empty_row_after=4)
	
	# Complexity Analysis
	doc.append(NewPage())
	cfg_list = []
	for codec in next(os.walk(result_path))[1]:  # get dirs
		with doc.create(Section(f'Complexity Analysis - (Codec Name: {codec.upper()})')):
			for codec_part in codecs_parts:
				path = result_path + '/' + codec + '/' + codec_part
				if os.path.exists(path):
					
					with doc.create(Subsection(f'{codec.upper()} {codec_part.upper()}\'s Complexity')):
						if codec_part == 'encoder':
							add_figures(codec, codec_part, doc, result_path)
						for config in next(os.walk(path))[1]:
							cfg_list.append(config)
							path = result_path + '/' + codec + '/' + codec_part + '/' + config + '/'
							classes_list = next(os.walk(path))[1]
							classes_list = sorted(classes_list, key=lambda x: x.rsplit('.')[-1])
							# print(classes_list)
							for class_name in classes_list:
								sub_sub_section_name = f'Config Name: {config}, Class Name: {class_name}'
								with doc.create(Subsubsection(sub_sub_section_name)):
									sub_sub_section_name = f'Config Name: {config},\n Class Name: {class_name}\n'
									path = result_path + '/' + codec + '/' + codec_part + '/' + config + '/' + class_name + '/'
									for analyzer_type in analyzing_types:
										# print(path)
										if analyzer_type == 'hotspots':
											hotspots_analysis(analyzer_type, doc, path, 2,
											                  caption=f"Hotspots By Function\n {sub_sub_section_name}")
										
										if analyzer_type == 'memory-consumption':
											hotspots_analysis(analyzer_type, doc, path, 2,
											                  caption=f"Memory Consumption\n {sub_sub_section_name}")
										
										if analyzer_type == 'performance-snapshot':
											selected_metrics = ['Elapsed Time', 'IPC', 'Effective Logical Core Utilization',
											                    'Effective Physical Core Utilization',
											                    'Microarchitecture Usage',
											                    'GPU Active Time']
											html_file_to_tables(analyzer_type, doc, path, selected_metrics,
											                    column_idx_to_sort=1,
											                    caption=f'Performance Snapshot\n {sub_sub_section_name}')
											
											selected_metrics = ['Elapsed Time', 'SP FLOPs', 'DP FLOPs', 'x87 FLOPs', 'Non-FP',
											                    'FP Arith/Mem Rd Instr. Ratio',
											                    'FP Arith/Mem Wr Instr. Ratio']
											html_file_to_tables(analyzer_type, doc, path, selected_metrics,
											                    column_idx_to_sort=1,
											                    caption=f'Instruction Mix\n {sub_sub_section_name}')
											
											doc.append(NewPage())
											selected_metrics = ['Elapsed Time', 'GPU Utilization when Busy', 'Active', 'Stalled',
											                    'Idle',
											                    'Occupancy']
											html_file_to_tables(analyzer_type, doc, path, selected_metrics,
											                    column_idx_to_sort=1,
											                    caption=f'GPU Usage\n {sub_sub_section_name}')
										
										if analyzer_type == 'memory-access':
											selected_metrics = ['CPU Time', 'L1 Bound', 'L2 Bound', 'L3 Bound',
											                    'DRAM Bound',
											                    'Store Bound', 'LLC Miss Count',
											                    'Average Latency (cycles)']
											html_file_to_tables(analyzer_type, doc, path, selected_metrics,
											                    column_idx_to_sort=1,
											                    caption=f'Memory Access Analysis\n {sub_sub_section_name}')
											
											doc.append(NewPage())
										
										if analyzer_type == 'uarch-exploration':
											selected_metrics = ['Elapsed Time', 'Clockticks', 'Instructions Retired',
											                    'CPI Rate', 'Bad Speculation', 'Branch Mispredict',
											                    'Vector Capacity Usage (FPU)']
											html_file_to_tables(analyzer_type, doc, path, selected_metrics,
											                    column_idx_to_sort=1,
											                    caption=f'Micro Architecture Exploration\n {sub_sub_section_name}')
											
											selected_metrics = ['Elapsed Time', 'Front-End Bound', 'Front-End Latency', 'ICache Misses',
											                    'ITLB Overhead', 'Branch Resteers',
											                    'Front-End Bandwidth']
											html_file_to_tables(analyzer_type, doc, path, selected_metrics,
											                    column_idx_to_sort=1,
											                    caption=f'Front-End Bound Analysis\n {sub_sub_section_name}')
											doc.append(NewPage())
											selected_metrics = ['Elapsed Time', 'Back-End Bound', 'L1 Bound',
											                    'L2 Bound', 'L3 Bound', 'DRAM Bound', 'Store Bound',
											                    'Store Latency']
											html_file_to_tables(analyzer_type, doc, path, selected_metrics,
											                    column_idx_to_sort=1,
											                    caption=f'Back-End Bound Analysis\n {sub_sub_section_name}')
											
											doc.append(NewPage())
	doc.generate_pdf("tab", clean_tex=False)


def add_figures(codec, codec_part, doc, result_path):
	for cls_seq in seq_class_names:
		fig_path = f'{result_path}/{codec}/{codec_part}/{codec}_{cls_seq}.pdf'
		if os.path.exists(fig_path):
			doc.append(NoEscape(r'\begin{figure}[H] \centering{\includegraphics[scale=1.2]{'))
			# print(fig_path)
			doc.append(NoEscape(fig_path))
			doc.append(NoEscape(r'}}\end{figure}'))
			doc.append(NewPage())


def html_file_to_tables(analyzer_type, doc, path, selected_metrics, column_idx_to_sort, caption):
	url = path + analyzer_type
	metrics_list = []
	for html_file in os.listdir(url):
		if (html_file.split('.')[-1]) == 'html':
			# print(url + '/' + html_file)
			metric_value = html_to_dict.get_data_from_html(url + '/' + html_file,
			                                               selected_metrics)
			metric_value_list = list(metric_value.values())
			split_html_name = html_file.split('_')
			# print(split_html_name)
			seq_name = split_html_name[0] + '\n QP = ' + split_html_name[-2].split('.')[0]
			metric_value_list.insert(0, seq_name)
			metrics_list.append(metric_value_list)
		# print(url + html_file)
		# print(metric_value)
	selected_metrics.insert(0, 'Seq Name')
	
	dict_to_pdf_table(doc, caption, selected_metrics, metrics_list)


def hotspots_analysis(analyzer_type, doc, path, no_of_column, caption):
	hotspots_csv = os.listdir(path + '/' + analyzer_type)
	data_list = csv_to_list(url=f"{path}/{analyzer_type}/{hotspots_csv[0]}",
	                        delimiter='\t')
	data_list = split_list(data_list, 0, no_of_column)
	split_csv_name = hotspots_csv[0].split('_')
	name = split_csv_name[0] + ', QP =' + split_csv_name[-1].split('.')[0]
	
	if analyzer_type == 'hotspots':  # add memory consumption too
		
		p = hotspots_csv[0].split('.')[:-1]
		by_class_csv_name = '_'.join(p) + '_by_class.csv'
		by_class_csv_path = path + '/' + analyzer_type + '/' + by_class_csv_name
		by_class_data_list = csv_to_list(by_class_csv_path)
		csv_to_pdf_table(doc, by_class_data_list, f'Hotpots By Class ({name})',
		                 no_of_rows=20, empty_row_after=4)
		doc.append(NewPage())
	
	csv_to_pdf_table(doc, data_list, f'{caption} ({name})', no_of_rows=20, empty_row_after=4)
	doc.append(NewPage())


if __name__ == "__main__":
	analyzing_types = ['hotspots', 'memory-consumption', 'performance-snapshot', 'memory-access', 'uarch-exploration']
	result_path = "/home/ridi/Desktop/Research_VVC_HM/results_2021_04_19_02_36_13"
	generate_pdf(result_path, analyzing_types)

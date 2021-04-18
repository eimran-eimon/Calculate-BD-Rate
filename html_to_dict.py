from bs4 import BeautifulSoup


# # selected_metrics = ['CPU Time', 'L1 Bound', 'L2 Bound', 'L3 Bound', 'DRAM Bound', 'Store Bound', 'LLC Miss Count', 'Average Latency (cycles)']
# selected_metrics = ['IPC', 'SP GFLOPS', 'DP GFLOPS', 'x87 GFLOPS', 'Average CPU Frequency']
#
# url = '/home/ridi/Desktop/Research_VVC_HM/' \
#       'results_2021_02_10_10_23_46/hm/encoder/' \
#       'encoder_intra_main.cfg/CLASS_A/performance-snapshot/' \
#       'Kimono_1920x1080_24.yuv_qp_22.html'


def get_data_from_html(url, selected_metrics):
	selected_metrics_value = {}
	other_metrics_name = []
	
	f = open(url, encoding="utf8")
	soup = BeautifulSoup(f, 'html.parser')
	f.close()
	metric_names = soup.findAll('span', class_='metric-name')
	
	for metric in metric_names:
		metric_name = metric.text.strip()[:-1]
		if metric_name in selected_metrics:
			metric_value = metric.find_next('span').contents[0]
			selected_metrics_value[metric_name] = metric_value
		else:
			other_metrics_name.append(metric_name)
	
	return selected_metrics_value

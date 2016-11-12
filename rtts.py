import subprocess
import re
import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends import backend_pdf

def run_ping(hostnames, num_packets, raw_ping_output_filename, aggregated_ping_output_filename):
	raw_ping_dict = {}
	aggregated_ping_dict = {}
	for host in hostnames:
		dropCount = 0
		raw_ping_dict[host] = [-1.0] * (num_packets - 1)
		pings_without_drops = np.array([])
		aggregated_ping_dict[host] = {}
		ping_process = subprocess.Popen(['ping', '-c', str(num_packets), host], stdout = subprocess.PIPE)
		while True:
			line = ping_process.stdout.readline()
			if not line:
				break
			numList = re.findall(r'=[^\s]+', str(line))
			numList = [float(x[1:]) for x in numList]
			if len(numList) == 3:
				if numList[0] == num_packets - 1:
					break
				else:
					if numList[1] > 0:
						raw_ping_dict[host][int(numList[0])] = numList[2]
						pings_without_drops = np.append(pings_without_drops, numList[2])
			dropCount = (num_packets - 1) - pings_without_drops.size
		with open(raw_ping_output_filename, 'w') as rpof:
			json.dump(raw_ping_dict, rpof)
		if pings_without_drops.size == 0:
			max_rtt = -1.0
			median_rtt = -1.0
			drop_rate = 100.0
		else:
			max_rtt = np.amax(pings_without_drops)
			median_rtt = np.median(pings_without_drops)
			drop_rate = float(dropCount)/float(num_packets - 1) * 100
		aggregated_ping_dict[host]['drop_rate'] = round(drop_rate, 3)
		aggregated_ping_dict[host]['max_rtt'] = round(max_rtt, 3)
		aggregated_ping_dict[host]['median_rtt'] = round(median_rtt, 3)
		with open(aggregated_ping_output_filename, 'w') as apof:
			json.dump(aggregated_ping_dict, apof)

#this function should take in a filename with the json formatted aggregated ping data and plot a CDF of the median RTTs for each website that responds to ping
def plot_median_rtt_cdf(agg_ping_results_filename, output_cdf_filename): 
	with open(agg_ping_results_filename) as agg_ping_results:
		data = json.load(agg_ping_results)
	vals = [x['median_rtt'] for x in data.values() if x['median_rtt'] != -1]
	median_rtts = np.array(vals)
	sorted_medians = np.sort(median_rtts)
	cdf_vals = np.arange(len(sorted_medians))/float(len(sorted_medians))
	plt.plot(sorted_medians, cdf_vals, label="Median Ping CDF")
	plt.legend(loc=4)
	plt.grid() 
	plt.xlabel("Time (ms)") 
	plt.ylabel("Cummulative fraction") 
	plt.savefig(output_cdf_filename)

# this function should take in a filename with the json formatted raw ping data for a particular hostname, and plot a CDF of the RTTs
def plot_ping_cdf(raw_ping_results_filename, output_cdf_filename): 
	with open(raw_ping_results_filename) as raw_ping_results:
		data = json.load(raw_ping_results)
	for host in data.keys():
		raw_rtts = np.array([x for x in data[host] if x != -1.0])
		sorted_rtts = np.sort(raw_rtts)
		cdf_vals = np.arange(len(sorted_rtts))/float(len(sorted_rtts))
		plt.plot(sorted_rtts, cdf_vals, label=host)
	plt.legend(loc=4)
	plt.grid() 
	plt.xlabel("Time (ms)")
	plt.ylabel("Cummulative fraction")
	plt.savefig(output_cdf_filename)


def main():
	top_100_sites = [x for x in open("./alexa_top_100", 'r').read().split('\n') if x != '']
	run_ping(top_100_sites, 11, 'new_a_raw.json', 'new_a_agg.json')
	part_b_sites = ['google.com', 'todayhumor.co.kr', '41.204.128.169', 'taobao.com']
	run_ping(part_b_sites, 501, 'new_b_raw.json', 'new_b_agg.json')


if __name__ == "__main__":
    main()


# rtts.run_ping(['tmall.com'], 10, 'tmall_raw.json', 'tmall_agg.json')
# rtts.plot_ping_cdf('rtt_b_raw.json', 'rtt_cdf_plot')
# rtts.plot_median_rtt_cdf('rtt_a_agg.json', 'median_cdf_plot')


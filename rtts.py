import subprocess
import re
import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends import backend_pdf

# All three numbers should be floats. If a website has a few dropped ping packets, do NOT include these in the median/max calculation. 
# If a website does not respond to pings at all, then max and median RTT should be -1.0, and drop rate should be 100.0.

def run_ping(hostnames, num_packets, raw_ping_output_filename, aggregated_ping_output_filename):
	raw_ping_dict = {}
	aggregated_ping_dict = {}
	for host in hostnames:
		dropCount = 0
		raw_ping_dict[host] = []
		pings_without_drops = np.array([])
		aggregated_ping_dict[host] = {}
		ping_process = subprocess.Popen(['ping', '-c', str(num_packets), host], stdout = subprocess.PIPE)
		currIndex = 0
		while True:
			# print 'hi'
			line = ping_process.stdout.readline()
			print 'raw line: '
			print line
			if not line:
				break
			numList = re.findall(r'=[^\s]+', str(line))
			numList = [float(x[1:]) for x in numList]
			# print 'num List:'
			# print numList
			if numList != []:
				if numList[0] == currIndex:
					currIndex += 1
				else:
					diff = int(numList[0] - currIndex)
					for i in range(diff):
						dropCount += 1
						raw_ping_dict[host].append(-1.0)
					currIndex = numList[0] + 1
				if numList[1] > 0:
					raw_ping_dict[host].append(numList[2])
					pings_without_drops = np.append(pings_without_drops, numList[2])
				else:
					raw_ping_dict[host].append(-1.0)
			# else:
			# 	currIndex += 1
			# 	raw_ping_dict[host].append(-1.0)
			else:
				if 'Request timeout' in line:
					dropCount += 1
					# print 'dropCount is: '
					# print dropCount
					currIndex += 1
					raw_ping_dict[host].append(-1.0)
		# print raw_ping_dict
		while len(raw_ping_dict[host]) < num_packets:
			raw_ping_dict[host].append(-1.0)
			dropCount += 1	
		if len(raw_ping_dict[host]) > num_packets:
			print 'ERROR'
		with open(raw_ping_output_filename, 'w') as rpof:
			json.dump(raw_ping_dict, rpof)
		if pings_without_drops.size == 0:
			max_rtt = -1.0
			median_rtt = -1.0
			drop_rate = 100.0
		else:
			max_rtt = np.amax(pings_without_drops)
			median_rtt = np.median(pings_without_drops)
			drop_rate = float(dropCount)/float(num_packets) * 100
		aggregated_ping_dict[host]['drop_rate'] = round(drop_rate, 3)
		aggregated_ping_dict[host]['max_rtt'] = round(max_rtt, 3)
		aggregated_ping_dict[host]['median_rtt'] = round(median_rtt, 3)
		with open(aggregated_ping_output_filename, 'w') as apof:
			json.dump(aggregated_ping_dict, apof)
		# print aggregated_ping_dict

# def max_and_median(lst):
# 	sorted_list = sorted(lst)
# 	maxVal = sorted_list[-1]
# 	if len(lst) % 2 == 1:
# 		medianVal = sorted_list[(len(lst) - 1)/2]
# 	else:
# 		mid = len(lst)/2
# 		medianVal = float(float(sorted_list[mid] + sorted_list[mid - 1]) / 2)
# 	return maxVal, medianVal


#this function should take in a filename with the json formatted aggregated ping data and plot a CDF of the median RTTs for each website that responds to ping
def plot_median_rtt_cdf(agg_ping_results_filename, output_cdf_filename): 
	with open(agg_ping_results_filename) as agg_ping_results:
		data = json.load(agg_ping_results)
	vals = [x['median_rtt'] for x in data.values() if x['median_rtt'] != -1]
	median_rtts = np.array(vals)
	sorted_medians = np.sort(median_rtts)
	cdf_vals = np.arange(len(sorted_medians))/float(len(sorted_medians))
	plt.plot(sorted_medians, cdf_vals, label="Median Ping CDF")
	plt.legend() # This shows the legend on the plot.
	plt.grid() # Show grid lines, which makes the plot easier to read.
	plt.xlabel("Time (ms)") # Label the x-axis.
	plt.ylabel("Cummulative fraction") # Label the y-axis.
	plt.savefig(output_cdf_filename)
	# filepath = output_cdf_filename
	# with backendpdf.PdfPages(filepath) as pdf:
 #      pdf.savefig()

# this function should take in a filename with the json formatted raw ping data for a particular hostname, and plot a CDF of the RTTs
def plot_ping_cdf(raw_ping_results_filename, output_cdf_filename): 
	with open(raw_ping_results_filename) as raw_ping_results:
		data = json.load(raw_ping_results)
	raw_rtts = np.array(data.values()[0])
	sorted_rtts = np.sort(raw_rtts)
	cdf_vals = np.arange(len(sorted_rtts))/float(len(sorted_rtts))
	print sorted_rtts.size
	print cdf_vals.size
	plt.plot(sorted_rtts, cdf_vals, label="Raw Ping CDF")
	plt.legend() # This shows the legend on the plot.
	plt.grid() # Show grid lines, which makes the plot easier to read.
	plt.xlabel("Time (ms)") # Label the x-axis.
	plt.ylabel("Cummulative fraction") # Label the y-axis.
	plt.savefig(output_cdf_filename)


def main():
	# top_100_sites = [x for x in open("./alexa_top_100", 'r').read().split('\n') if x != '']
	# run_ping(top_100_sites, 10, 'rtt_a_raw.json', 'rtt_a_agg.json')
	part_b_sites = ['google.com', 'todayhumor.co.kr', 'zanvarsity.ac.tz', 'taobao.com']
	run_ping(part_b_sites, 500, 'rtt_b_raw.json', 'rtt_b_agg.json')


if __name__ == "__main__":
    main()


# rtts.run_ping(['tmall.com'], 10, 'tmall_raw.json', 'tmall_agg.json')
# rtts.plot_ping_cdf('first.json', '')
# rtts.plot_median_rtt_cdf('rtt_a_agg.json', 'median_cdf_plot')

#re.findall(r'=[^\s]+', '64 bytes from 216.58.194.206: icmp_seq=0 ttl=54 time=2.561 ms')
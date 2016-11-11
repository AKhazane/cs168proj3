import json 
import numpy as np
import matplotlib.pyplot as plt

def get_average_ttls(filename):
	with open(filename) as json_file:
		dig_calls = json.load(json_file)
	averages = []
	for dig in dig_calls:
		root_servers = np.array([])
		tld_servers = np.array([])
		ns_servers = np.array([])
		terminating_servers = np.array([])
		for query in dig['Queries']:
			for answer in query['Answers']:
				if answer['Type'] == 'NS':
					if answer['Queried name'] == '.':
						root_servers = np.append(root_servers, answer['TTL'])
					elif answer['Queried name'].count(".") == 1:
						tld_servers = np.append(tld_servers, answer['TTL'])
					else:
						ns_servers = np.append(ns_servers, answer['TTL'])
				else:
					terminating_servers = np.append(terminating_servers, answer['TTL'])
		new_averages = [np.mean(root_servers), np.mean(tld_servers), np.mean(ns_servers), np.mean(terminating_servers)]
		if averages == []:
			averages = np.array([new_averages])
		else: 
			averages = np.concatenate((averages, np.array([new_averages])), axis=0)
	final_averages = np.mean(np.array(averages), axis=0)
	return final_averages.tolist()

def get_average_times(filename):
	with open(filename) as json_file:
		dig_calls = json.load(json_file)
	total_list = np.array([])
	final_list = np.array([])
	for dig in dig_calls:
		currTotal = 0
		currFinal = 0
		for query in dig['Queries']:
			currTotal += float(query['Time in millis'])
			for answer in query['Answers']:
				if answer['Type'] != 'NS':
					currFinal += float(query['Time in millis'])
					break
		final_list = np.append(final_list, currFinal)
		total_list = np.append(total_list, currTotal)
	avg_total = round(np.mean(total_list), 3)
	avg_final = round(np.mean(final_list), 3)
	return [avg_total, avg_final]

def generate_time_cdfs(json_filename, output_filename):
	with open(json_filename) as json_file:
		dig_calls = json.load(json_file)
	total_list = np.array([])
	final_list = np.array([])
	for dig in dig_calls:
		currTotal = 0
		currFinal = 0
		for query in dig['Queries']:
			currTotal += float(query['Time in millis'])
			for answer in query['Answers']:
				if answer['Type'] != 'NS':
					currFinal += float(query['Time in millis'])
					break
		final_list = np.append(final_list, currFinal)
		total_list = np.append(total_list, currTotal)
	sorted_final_times = np.sort(final_list)
	print sorted_final_times
	print len(sorted_final_times)
	final_cdf_vals = np.arange(len(sorted_final_times))/float(len(sorted_final_times))
	print final_cdf_vals
	plt.plot(sorted_final_times, final_cdf_vals, label='Time to resolve final request')
	sorted_total_times = np.sort(total_list)
	print sorted_total_times
	print len(sorted_total_times)
	total_cdf_vals = np.arange(len(sorted_total_times))/float(len(sorted_total_times))
	plt.plot(sorted_total_times, total_cdf_vals, label='Time to resolve site')
	plt.legend(loc=4)
	plt.grid() 
	plt.xlabel("Time (ms)")
	plt.ylabel("Cummulative fraction")
	plt.savefig(output_filename)



def main():
	# print get_average_ttls('examples/dig_sample_output.json')
	# print get_average_times('examples/dig_sample_output.json')
	generate_time_cdfs('examples/dig_sample_output.json', 'time_cdfs')

if __name__ == "__main__":
    main()
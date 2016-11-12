import subprocess
import time
import json
import re
import os
import utils
import numpy as np
import codecs
import matplotlib.pyplot as plt

def run_dig(hostname_filename, output_filename, dns_query_server=None):
	dig_json = []
	if dns_query_server == None:
		with open(hostname_filename, "r") as f:
			with open("dig_shell_output", "w") as f1:
				for line in f:
					i = 0
					while (i < 5):
						command = "dig +trace +tries=1 +nofail +nodnssec {0}".format(line)
						subprocess.call(command.split(), stdout=f1)
						i+=1
		with open("dig_shell_output", "r") as f:
			f.readline()
			hostname_results = {utils.NAME_KEY: None, utils.SUCCESS_KEY: True, utils.QUERIES_KEY : []}
			answer = {utils.QUERIED_NAME_KEY: None, utils.ANSWER_DATA_KEY: None, utils.TYPE_KEY: None, utils.TTL_KEY: None}
			query =  {utils.TIME_KEY: None, utils.ANSWERS_KEY: []}
			failed_test = False
			for line in f:
				line = line.split()
				print line
				if len(line) == 0:
						if query[utils.TIME_KEY] != None:
							hostname_results[utils.QUERIES_KEY].append(query)
							query =  {utils.TIME_KEY: None, utils.ANSWERS_KEY: []}
				elif line[0] == ";;" and line[1] == "connection":
					hostname_results[utils.SUCCESS_KEY] = False
					del hostname_results[utils.QUERIES_KEY]
					dig_json.append(hostname_results)
					hostname_results = {utils.NAME_KEY: None, utils.SUCCESS_KEY: True, utils.QUERIES_KEY : []}
					failed_test = True
				elif line[0] == ";" and line[1] == "<<>>":
					if hostname_results[utils.NAME_KEY] != None:
						dig_json.append(hostname_results) 
						hostname_results = {utils.NAME_KEY: None, utils.SUCCESS_KEY: True, utils.QUERIES_KEY : []}
					hostname_results[utils.NAME_KEY] = line[len(line) - 1]
					failed_test = False
				elif not failed_test:
					if line[0] == ";;" and line[1] == "Received":
						query[utils.TIME_KEY] = line[7] 		
					elif line[1] != "global":
						if line[3] == "A" or line[3] == "CNAME" or line[3] == "NS":
							answer = {utils.QUERIED_NAME_KEY: line[0], utils.ANSWER_DATA_KEY: line[len(line) - 1], 
							utils.TYPE_KEY: line[3], utils.TTL_KEY: line[1]}
							query[utils.ANSWERS_KEY].append(answer)
						else:
							hostname_results[utils.SUCCESS_KEY] = False
							del hostname_results[utils.QUERIES_KEY]
							dig_json.append(hostname_results)
							hostname_results = {utils.NAME_KEY: None, utils.SUCCESS_KEY: True, utils.QUERIES_KEY : []}
							failed_test = True
		dig_json.append(hostname_results)
		with open(output_filename, "w") as f2:
			f2.write(json.dumps(dig_json))
	else:
		with open(hostname_filename, "r") as f:
			with open("dig_shell_output", "w") as f1:
				for line in f:
					i = 0
					while (i < 5):
						command = "dig {0} @{1}".format(line, dns_query_server)
						subprocess.call(command.split(), stdout=f1)
						i+=1
		with open("dig_shell_output", "r") as f2:
			f2.readline()
			hostname_results = {utils.NAME_KEY: None, utils.SUCCESS_KEY: True, utils.QUERIES_KEY : []}
			answer = {utils.QUERIED_NAME_KEY: None, utils.ANSWER_DATA_KEY: None, utils.TYPE_KEY: None, utils.TTL_KEY: None}
			query =  {utils.TIME_KEY: None, utils.ANSWERS_KEY: []}
			failed_test = False 
			in_answers = False
			for line in f2:
				line = line.split()
				print line
				if len(line) > 0:
					if line[0] == ";" and line[1] == "<<>>":
						if hostname_results[utils.NAME_KEY] != None:
							dig_json.append(hostname_results) 
							hostname_results = {utils.NAME_KEY: None, utils.SUCCESS_KEY: True, utils.QUERIES_KEY : []}
						hostname_results[utils.NAME_KEY] = line[len(line) - 2]
					elif line[0] == ";;" and line[1] == "->>HEADER<<-":
						if line[5] != "NOERROR,":
							hostname_results[utils.SUCCESS_KEY] = False
							del hostname_results[utils.QUERIES_KEY]
							dig_json.append(hostname_results)
							hostname_results = {utils.NAME_KEY: None, utils.SUCCESS_KEY: True, utils.QUERIES_KEY : []}
							failed_test = True
					elif not failed_test:
						if line[0] == ";;" and (line[1] == "ANSWER" or line[1] == "ADDITIONAL"):
							in_answers = True
						elif in_answers:
							if line[3] == "A" or line[3] == "CNAME" or line[3] == "NS":
								answer = {utils.QUERIED_NAME_KEY: line[0], utils.ANSWER_DATA_KEY: line[len(line) - 1], 
								utils.TYPE_KEY: line[3], utils.TTL_KEY: line[1]}
								query[utils.ANSWERS_KEY].append(answer)
							else:
								hostname_results[utils.SUCCESS_KEY] = False
								del hostname_results[utils.QUERIES_KEY]
								dig_json.append(hostname_results)
								hostname_results = {utils.NAME_KEY: None, utils.SUCCESS_KEY: True, utils.QUERIES_KEY : []}
								failed_test = True
						elif line[0] == ";;" and line[1] == "Query":
							query[utils.TIME_KEY] = line[3] 
							hostname_results[utils.QUERIES_KEY].append(query) 
							query = {utils.TIME_KEY: None, utils.ANSWERS_KEY: []}
				else:
					in_answers = False
		dig_json.append(hostname_results)
		with open(output_filename, "w") as f2:
			f2.write(json.dumps(dig_json))
					


def get_average_ttls(filename):
	with open(filename) as json_file:
		dig_calls = json.load(json_file)
	averages = []
	for dig in dig_calls:
		print dig.keys()
		root_servers = np.array([])
		tld_servers = np.array([])
		ns_servers = np.array([])
		terminating_servers = np.array([])
		print dig.keys()
		if dig[utils.SUCCESS_KEY]:
			for query in dig[utils.QUERIES_KEY]:
				for answer in query[utils.ANSWERS_KEY]:
					if answer[utils.TYPE_KEY] == 'NS':
						if answer[utils.QUERIED_NAME_KEY] == '.':
							root_servers = np.append(root_servers, answer[utils.TTL_KEY])
						elif answer[utils.QUERIED_NAME_KEY].count(".") == 1:
							tld_servers = np.append(tld_servers, answer[utils.TTL_KEY])
						else:
							ns_servers = np.append(ns_servers, answer[utils.TTL_KEY])
					else:
						terminating_servers = np.append(terminating_servers, answer[utils.TTL_KEY])
			print
			new_averages = [np.mean(root_servers.astype(float)), np.mean(tld_servers.astype(float)), np.mean(ns_servers.astype(float)), np.mean(terminating_servers.astype(float))]
			if averages == []:
				averages = np.array([new_averages])
			else: 
				averages = np.concatenate((averages, np.array([new_averages])), axis=0)
		final_averages = np.mean(np.array(averages), axis=0) / 1000 
		return final_averages.tolist()

def checkRoot(name):
	return name == "."

def checkTLD(name):
	return name.count('.') == 1 and len(name) > 1
def get_average_times(filename):
	with open(filename) as json_file:
		dig_calls = json.load(json_file)
	total_list = np.array([])
	final_list = np.array([])
	for dig in dig_calls:
		currTotal = 0
		currFinal = 0
		if dig[utils.SUCCESS_KEY]:
			for query in dig[utils.QUERIES_KEY]:
				currTotal += float(query[utils.TIME_KEY])
				for answer in query[utils.ANSWERS_KEY]:
					if answer[utils.TYPE_KEY] != 'NS':
						currFinal += float(query[utils.TIME_KEY])
						break
			final_list = np.append(final_list, currFinal)  
			total_list = np.append(total_list, currTotal) 
 	avg_final = round(np.mean(total_list), 3)
 	avg_total = round(np.mean(final_list), 3)
	return [avg_total, avg_final] 

def generate_time_cdfs(json_filename, output_filename):
	with open(json_filename) as json_file:
		dig_calls = json.load(json_file)
	total_list = np.array([])
	final_list = np.array([])
	for dig in dig_calls:
		currTotal = 0
		currFinal = 0
		if dig[utils.TIME_KEY]:
			for query in dig[utils.QUERIES_KEY]:
				currTotal += float(query[utils.TIME_KEY])
				for answer in query[utils.ANSWERS_KEY]:
					if answer[utils.TYPE_KEY] != 'NS':
						currFinal += float(query[utils.TIME_KEY])
						break
			final_list = np.append(final_list, currFinal)
			total_list = np.append(total_list, currTotal)
	# print final_list 
	# print total_list
	sorted_final_times = np.sort(final_list)
	final_cdf_vals = np.arange(len(sorted_final_times))/float(len(sorted_final_times))
	plt.plot(sorted_final_times, final_cdf_vals, label='Time to resolve final request')
	sorted_total_times = np.sort(total_list)
	print sorted_total_times
	total_cdf_vals = np.arange(len(sorted_total_times))/float(len(sorted_total_times))
	print total_cdf_vals
	plt.plot(sorted_total_times, total_cdf_vals, label='Time to resolve site')
	plt.legend(loc=4)
	plt.grid(True) 
	plt.xlabel("Time (ms)")
	plt.ylabel("Cummulative fraction")
	plt.savefig(output_filename)

def count_different_dns_responses(filename1,filename2):
	different_entries = set()
	different_team_entries = set()
	different_host = {}
	with open(filename1, "r") as f1:
		with open(flename2, "r") as f2:
			dig_json1 = json.load(f1)
			dig_json2 = json.load(f2)
			for hostname in dig_json1:
				if hostname[utils.SUCCESS_KEY]:
					for query in hostname[utils.QUERIES_KEY]:
						responses = set()
						for response in query[utils.ANSWERS_KEY]:
							name = response[utils.ANSWER_DATA_KEY]
							types = response[utils.TYPE_KEY]
							data = response[utils.ANSWER_DATA_KEY]
							if checkRoot(name) or checkTLD(name) or (types != "A" or types != "CNAME"):
								continue
							responses.add(data)
						if name not in different_host:
							different_host[name] = responses
						elif different_host[name] != responses:
							different_entries.add(name)
			for hostname in dig_json2:
				if hostname[utils.SUCCESS_KEY]:
					for query in hostname[utils.QUERIES_KEY]:
						responses = set()
						for response in query[utils.ANSWERS_KEY]:
							name = response[utils.ANSWER_DATA_KEY]
							types = response[utils.TYPE_KEY]
							data = response[utils.ANSWER_DATA_KEY]
							if checkRoot(name) or checkTLD(name) or (types != "A" or types != "CNAME"):
								continue
							responses.add(data)
						if name in different_host and different_host[name] != responses:
							different_team_entries.add(name)
	first_value = len(different_host)
	second_value = len(different_team_entries | different_team_entries)
	return [first_value, second_value]





# run_dig("alexa_top_100", "dns_output_other_server.json", "188.94.241.79")
print get_average_ttls("dns_output_1.json")
# generate_time_cdfs("dns_output_1.json", "plot")
# print get_average_times("dns_output_other_server.json")
import subprocess
import time
import json
import re
import os
import utils
dig_json = [] 
def run_dig(hostname_filename, output_filename, dns_query_server=None):
	global dig_json
	if dns_query_server == None:
		with open(hostname_filename, "r") as f:
			for line in f:
				i = 0
				while (i < 5):
					command = "dig +trace +tries=1 +nofail +nodnssec {0}".format(line)
					subprocess.call(command.split(), stdout=f)
					i+=1


#{"Name": ___, "Success": ____, "Queries" : [{"Time in millis": ___, 
#											 "Queries": }]}

def parse_dig(input_file):
	global dig_json
	hostname_results = {utils.NAME_KEY: "www.google.com", utils.SUCCESS_KEY: None, utils.QUERIES_KEY : []}
	dig_json.append(hostname)
	with open(input_file, "r") as f:
		f.readline()
		answer = ""
		query = ""
		for line in f:
			if line[0] == ";;" and line[1] != "Received":
				#my output has ended, so I need to create a new query
				query = {utils.TIME_KEY: None, utils.ANSWERS_KEY: []}
			elif line[0] == ";;" and line[1] == "Received":
				hostname_results[utils.QUERIES_KEY].append(query)
			elif line[0] == ".":
				print("went inside")
				if (line[3] != "A" )
				answer = {utils.QUERIED_NAME_KEY: line[0], utils.ANSWER_KEY_DATA: line[len(line) - 1], 
				utils.TYPE_KEY: line[3], utils.TTL_KEY: line[1]}
				query[utils.ANSWERS_KEY].append(answer)
	with open("example.txt", "w") as f2:
		f2.write(json.dumps(dig_json, indent = 2))



parse_dig("dig_shell")
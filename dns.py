import subprocess
import time
import json
import re
import os
import utils


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
					
				#if first index is ; and second is <<>> then beginning of new query
					# add that query to the json dictionary
					# reset time

#{"Name": ___, "Success": ____, "Queries" : [{"Time in millis": ___, 
#											 "Queries": }]}

# def parse_dig(input_file):
	# hostname_results = {utils.NAME_KEY: "www.google.com", utils.SUCCESS_KEY: True, utils.QUERIES_KEY : []}
	# dig_json.append(hostname)
	# with open(input_file, "r") as f:
	# 	f.readline()
	# 	answer = ""
	# 	query = ""
	# 	for line in f:
	# 		line = line.split()
	# 		print line 
	# 		if line[0] == ";;" and line[1] != "Received":
	# 			#my output has ended, so I need to create a new query
	# 			query = {utils.TIME_KEY: None, utils.ANSWERS_KEY: []}
	# 		elif line[0] == ";;" and line[1] == "Received":
	# 			hostname_results[utils.QUERIES_KEY].append(query)
	# 		elif line[0] == ".":
	# 			print("went inside")
	# 			if line[3] != "A" or line[3] != "CNAME" or line[3] != "NS":
	# 				answer = {utils.QUERIED_NAME_KEY: line[0], utils.ANSWER_KEY_DATA: line[len(line) - 1], 
	# 				utils.TYPE_KEY: line[3], utils.TTL_KEY: line[1]}
	# 				query[utils.ANSWERS_KEY].append(answer)
	# 			else:
	# 				hostname_results[utils.SUCCESS_KEY] = False
	# 				del hostname_results[2]


	



run_dig("alexa_top_100", "dns_output_other_server.json", "188.94.241.79")
# parse_dig("dig_shell")o
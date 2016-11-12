import subprocess
import time
import json
import re
import os

# count how many stars you get after stripping and splitting. If equal to # of packets, then create a$
# y.split("ms")[3].strip().split()...iterate like this to get multiple routers on one hop
traceroute_json = {}
def run_traceroute(hostnames, num_packets, output_filename):
        global traceroute_json
        # traceroute_json["timestamp"] = time.time()
        with open(output_filename, "w") as f:
                for hostname in hostnames:
                        traceroute_json[hostname] = []
                        command = "traceroute -A -q {0} {1}".format(num_packets, hostname)
                        subprocess.call(command.split(), stdout=f)
                # f.write(json.dumps(traceroute_json, indent=4))


def parse_traceroute(raw_traceroute_filename, output_filename):
        # match everything in parantheses (p = re.compile('\(([^\)]+)\)')
        # match everything in brackets (p = re.compile('\[([^\)]+)\]')
        # unsure of how to extract out the hop names
        global traceroute_json
        current_hostname = ""
        with open(raw_traceroute_filename, 'r') as f1:
                for line in f1: #parse all hops
                        line = line.strip()
                        if line.startswith("traceroute"):
                                line = line.split()
                                current_hostname = line[2] 
                        else:
                                packets = []
                                ip_check = [] 
                                parse = line.split("ms")
                                parse[0] = parse[0].strip().split()
                                parse[0].pop(0)
                                parse[0] = " ".join(parse[0])
                                for hop in parse:
                                        info = {"name": "None", "ip": "None", "ASN": "None"}
                                        line2 = hop.strip().split()
                                        if len(line2) >  2:
                                                while(len(line2) != 0 and (line2[0] == " " or line2[0] == "*" or line2[0] == "*,")):
                                                        line2.pop(0)
                                                if len(line2) > 2:
                                                        p = re.compile('\(([^\)]+)\)')
                                                        info["name"] = line2[0]
                                                        if len(p.findall(line2[1])) == 0:
                                                                if info['name'] not in ip_check:
                                                                        info['ip'] = info['name']
                                                                        info = retrieve_ASN(line2, info, 1)
                                                                        packets.append(info)
                                                        elif p.findall(line2[1])[0] not in ip_check:
                                                                ip_check.append(p.findall(line2[1])[0])
                                                                info["ip"] = p.findall(line2[1])[0]
                                                                info = retrieve_ASN(line2, info, 2)
                                                                packets.append(info)
                                        elif len(line2) > 0:
                                                p = re.compile("^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$")
                                                # print line2
                                                if len(p.findall(line2[0])) > 0:
                                                        print ("yep")
                                                        info['ip'] = p.findall(line2[0])[0]
                                                        info['name'] = info['ip']
                                                        packets.append(info)
                                if (len(packets) == 0):
                                        traceroute_json[current_hostname].append([info])
                                else:
                                        traceroute_json[current_hostname].append(packets)


        with open(output_filename, "a") as f2:
                f2.write(json.dumps(traceroute_json))



def retrieve_ASN(line2, info, index):
        print line2 
        p = re.compile('\[([^\)]+)\]')
        if len(p.findall(line2[index])) != 0:
                print("we good fam")
                intermediate = p.findall(line2[index])[0]
                p = re.compile(r'\d+')
                check = p.findall(intermediate)
                if len(check) == 0:
                        info["ASN"] = str(None)
                elif len(check) == 1 and check[0] == 0:
                        info["ASN"] = str(None)
                        value = "" 
                else:
                        value = ""
                        for asn_number in check:
                                value += str(asn_number) + "/"
                        value = value[:-1] 
                        info['ASN'] = value
        return info 
os.chdir(os.getcwd())
run_traceroute(["google.com", "facebook.com", "www.berkeley.edu", "allspice.lcs.mit.edu", "todayhumor.co.kr", "www.city.kobe.lg.jp", "www.vutbr.cz", "zanvarsity.ac.tz"], 5, "traceroute.txt")
parse_traceroute("traceroute.txt", 'tr_a.json')
# run_traceroute(["tpr-route-server.saix.net", "route-server.ip-plus.net", "route-views.oregon-ix.net", "route-views.on.bb.telus.com"], 3, "traceroute3.txt")
# parse_traceroute("traceroute3.txt", 'tr_b.json')
# traceroute_json['tpr-route-server.saix.net'] = []
# traceroute_json['route-views.on.bb.telus.com'] = []
# traceroute_json['route-server.ip-plus.net'] = []
# traceroute_json['route-views.oregon-ix.net'] = []

# parse_traceroute("traceroute2.txt", 'tr_b.json')
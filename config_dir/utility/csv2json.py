import json
import glob
import os

csv_files = [f for f in glob.glob("../csv_data/*.csv")]
print(csv_files)

for file in csv_files:
	f = open(file, "r")
	rf = f.read()
	f.close()

	srf = rf.split("\n")
	for k in range(len(srf)):
		if srf[k] == '':
			del srf[k]
	for k in range(len(srf)):
		srf[k] = srf[k].split(',')

	awal = srf[0]
	del srf[0]

	kamus = dict()

	daerah = []
	for d in srf:
		if d[0] not in daerah:
			daerah.append(d[0])
	
	for de in daerah:
		kamus[de] = dict()

	for w in range(len(srf)):
		kamus[srf[w][0]][srf[w][2]] =  srf[w][3]

	name_json = "../utility/" + file.split("/")[-1].split('.')[0] + ".json"
	file_json = open(name_json, "w")
	json.dump(kamus, file_json)
	file_json.close()

	print("saved: ", name_json, '\n')

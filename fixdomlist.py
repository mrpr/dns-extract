import os.path
import csv, json

with open('domdata.json', 'r') as fp:
    ddata = json.load(fp)

with open(os.path.expanduser('~/volvo/dns/del_records.csv'), 'r') as fp:
    csvr = csv.reader(fp, delimiter=' ')
    for item in csvr:
        item = item[0]
        try:
            ind = item.rindex('volvo')

        except:
            ind = item[:item.rfind('.')].rfind('.') + 1

        entry = item[:ind-1]
        domain = item[ind:]
        # print('%s ::: %s'%(entry, domain))

        if domain in ddata:
            for rtype, records in ddata[domain].items():
                for record in records:
                    if record['Key'] == entry:
                        print('%s %s %s %s'%(entry, rtype, domain, record['Value']))

print('ende')

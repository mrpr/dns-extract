import ultra_rest_client
import requests
import json
import sys

apidom = 'restapi.ultradns.com'
user = 'ronnywikh',

if len(sys.argv) == 4:
    sys.stdout.flush()
    apikey, ukey, pwd = sys.argv[1:4]
else:
    print('Incorrect syntax. Usage: getdomdata.py <csc api key> <csc api token> <ultradns password>')
    sys.exit(1)

def getcsc():
    session = requests.Session()
    session.headers.update({'apikey': apikey,
                            'Authorization': 'Bearer %s'%(ukey,)})

    domdata = session.get('https://apis.cscglobal.com/dbs/api/v2/domains')

    domdict = json.loads(domdata.content)

    ddata = {}

    domlist = domdict.get('domains', [])

    print('Found %d domains in CSC registry'%len(domlist))
    sys.stdout.flush()
    dcount = 0

    for domain in domlist:
        dcount += 1
        zinfo = {}
        if dcount % 50 == 0:
            print(dcount)
            sys.stdout.flush()
        ddata[domain['qualifiedDomainName']] = zinfo

        zonedata = session.get('https://apis.cscglobal.com/dbs/api/v2/zones/%s'%domain['qualifiedDomainName'])
        zonedict = json.loads(zonedata.content)
        for zone in sorted(zonedict.get('mx', []), key = lambda z: z['priority']):
            record = { 'Key': zone['key'],
                       'Priority': zone['priority'],
                       'TTL': zone['ttl'],
                       'Value': zone['value'] }
            zinfo.setdefault('MX', []).append(record)
        for ztype in ('txt', 'a', 'aaaa',   'cname'):
            for zone in sorted(zonedict.get(ztype, []), key=lambda z: z['key']):
                record = { 'Key': zone['key'],
                           'TTL': zone['ttl'],
                           'Value': zone['value'] }
                zinfo.setdefault(ztype.upper(), []).append(record)

    print('Done extracting CSC domains')
    sys.stdout.flush()
    return ddata

def getultradns():
    ddata = {}
    
    c = ultra_rest_client.RestApiClient(user, pwd, False, apidom)

    ad = c.get_account_details()
    zones = c.get_zones_of_account(ad['accounts'][0]['accountName'])
    print('Extracting %d zones from ultradns.'%len(zones['zones']))
    sys.stdout.flush()
    for zone in zones['zones']:
        zinfo = {}
        zname = zone['properties']['name']
        ddata[zname[:-1]] = zinfo

        zdata = c.get_rrsets(zname)
        for item in zdata['rrSets']:
            rtype = item['rrtype'].split(' ')[0]
            key = item['ownerName'].split(zname)[0][:-1]
            ttl = item['ttl']
            if rtype in ('A', 'AAAA', 'CNAME', 'TXT'):
                record = { 'Key': key,
                           'TTL': ttl,
                           'Value': item['rdata'][0] }
                zinfo.setdefault(rtype, []).append(record)
            if rtype == 'MX':
                for mxv in item['rdata']:
                    priority, value = mxv.split(' ')
                    record = { 'Key': key,
                               'TTL': ttl,
                               'Priority': priority,
                               'Value': value }
                    zinfo.setdefault(rtype, []).append(record)

    print('Extraction from ultradns done.')
    sys.stdout.flush()
    return ddata

ddata = getcsc()
ddata.update(getultradns())
print('Dumping data to file domdata.json')
sys.stdout.flush()
with open('domdata.json', 'w') as fp:
    json.dump(ddata, fp, indent=2)
print('Done.')
sys.stdout.flush()


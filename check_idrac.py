#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
from enum import Enum
import sys
import json
import redfish
import atexit
import warnings

epilog = """
Checking status of DELL iDRAC management controllers
"""


class Colors(Enum):
    NAGIOS_OK = '#23a34e'
    NAGIOS_CRITICAL = '#ff5b33'
    NAGIOS_WARNING = '#ffa500'
    NAGIOS_UNKNOWN = '#eb7d34'


class ExitCodes(Enum):
    NAGIOS_OK = 0
    NAGIOS_WARNING = 1
    NAGIOS_CRITICAL = 2
    NAGIOS_UNKNOWN = 3


warnings.filterwarnings("ignore")


def args():
    parser = argparse.ArgumentParser(
        description='Check DELL iDRAC Management Controllers',
        epilog=epilog,
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("-H", "--hostname", dest='HOSTNAME', type=str, required=True,
                        help='HOSTNAME or IP of target device')
    parser.add_argument("-U", "--user", dest='USER', type=str,
                        default='monitor',
                        help='Monitoring user')
    parser.add_argument("-P", "--password", dest='PASSWORD', type=str, required=True,
                        help='Monitoring user password')
    parser.add_argument("-t", "--timeout", dest='TIMEOUT', type=int,
                        default=10,
                        help='Timeout in seconds')
    parser.add_argument("--dumpresponse", dest='DUMPRESPONSE',
                        action='store_true',
                        help='Dump the response into a <mode>_response.json file.')
    parser.add_argument('--mode', dest='MODE', type=str, required=True,
                        choices=['health', 'controller',
                                 'powersupply', 'disk', 'thermal', 'memory', 'dellsystem', 'version'],
                        help='Select the mode you want..')
    parsed, unknown = parser.parse_known_args()
    for arg in unknown:
        if arg.startswith(("-", "--")):
            # you can pass any arguments to add_argument
            parser.add_argument(arg, type=str)

    return parser.parse_args()


def mode_disk(session, args):
    state = "OK"
    exitcode = [ExitCodes.NAGIOS_OK]
    output_list = [
        '<tr><th>Type</th><th>Name</th><th>Health</th></tr>']
    component_counter = 0
    ok_counter = 0
    unknown_counter = 0
    warn_counter = 0

    response = query_api(
        session, '/Systems/System.Embedded.1/Storage?$expand=*($levels=1)', args)
    controllers = response['Members']
    for controller in controllers:
        controller_id = controller['@odata.id']
        query_endpoint = controller_id+"?$select=Drives"
        response = query_api(session, query_endpoint, args)
        members = response['Drives']

        for r in members:
            disk = query_api(session, r['@odata.id'], args)
            status = disk['Status']['HealthRollup']
            if status != None:
                status = status.lower()
            else:
                status = "Empty"
            if status in ['ok']:
                ok_counter += 1
                color = Colors.NAGIOS_OK.value
            elif status in [None, 'Empty']:
                color = Colors.NAGIOS_UNKNOWN.value
                unknown_counter += 1
                exitcode.append(ExitCodes.NAGIOS_UNKNOWN.value)
            elif status in ['Warning']:
                color = Colors.NAGIOS_WARNING.value
                warn_counter += 1
                exitcode.append(ExitCodes.NAGIOS_WARNING.value)
            else:
                state = "CRITICAL"
                exitcode.append(ExitCodes.NAGIOS_CRITICAL.value)
                color = Colors.NAGIOS_CRITICAL.value
            component_counter += 1
            output_list.append('<tr><td>{}</td><td>{}</td><td style="background-color:{}">{}</td></tr>'.format(
                disk['@odata.type'], disk['Name'], color, status.upper()))
    output_html = "<table>{}</table>".format("".join(output_list))
    output = "{}: {}/{} disk(s) are healthy. {} without status.\n{}".format(
        state, ok_counter+unknown_counter+warn_counter, component_counter, unknown_counter, output_html)
    return output, exitcode


def mode_powersupply(session, args):
    state = "OK"
    exitcode = [0]
    output_list = [
        '<tr><th>Type</th><th>Name</th><th>Health</th></tr>']
    component_counter = 0
    ok_counter = 0
    unknown_counter = 0
    warn_counter = 0
    response = query_api(session, '/Chassis/System.Embedded.1/Power', args)
    members = response['PowerSupplies']

    for r in members:
        status = r['Status']['Health']
        if status != None:
            status = status.lower()
        else:
            status = "Empty"
        if status in ['ok']:
            ok_counter += 1
            color = '#23a34e'
        elif status in [None, 'Empty']:
            color = '#eb7d34'
            unknown_counter += 1
            exitcode.append(ExitCodes.NAGIOS_UNKNOWN.value)
        elif status in ['Warning']:
            color = '#ffa500'
            warn_counter += 1
            exitcode.append(ExitCodes.NAGIOS_WARNING.value)
        else:
            state = "CRITICAL"
            exitcode.append(ExitCodes.NAGIOS_CRITICAL.value)
            color = '#ff5b33'
        component_counter += 1
        output_list.append('<tr><td>{}</td><td>{}</td><td style="background-color:{}">{}</td></tr>'.format(
            r['@odata.type'], r['Name'], color, status.upper()))
    output_html = "<table>{}</table>".format("".join(output_list))
    output = "{}: {}/{} powersupplies are healthy. {} without status.\n{}".format(
        state, ok_counter+unknown_counter+warn_counter, component_counter, unknown_counter, output_html)
    return output, exitcode


def mode_memory(session, args):
    state = "OK"
    exitcode = [0]
    output_list = [
        '<tr><th>Type</th><th>Name</th><th>Health</th></tr>']
    component_counter = 0
    ok_counter = 0
    unknown_counter = 0
    warn_counter = 0
    response = query_api(
        session, '/Systems/System.Embedded.1/Memory?$expand=*($levels=1)', args)
    members = response['Members']

    for r in members:
        status = r['Status']['Health']
        if status != None:
            status = status.lower()
        else:
            status = "Empty"
        if status in ['ok']:
            ok_counter += 1
            color = '#23a34e'
        elif status in [None, 'Empty']:
            color = '#eb7d34'
            unknown_counter += 1
            exitcode.append(ExitCodes.NAGIOS_UNKNOWN.value)
        elif status in ['Warning']:
            color = '#ffa500'
            warn_counter += 1
            exitcode.append(ExitCodes.NAGIOS_WARNING.value)
        else:
            state = "CRITICAL"
            exitcode.append(ExitCodes.NAGIOS_CRITICAL.value)
            color = '#ff5b33'
        component_counter += 1
        output_list.append('<tr><td>{}</td><td>{}</td><td style="background-color:{}">{}</td></tr>'.format(
            r['@odata.type'], r['Name'], color, status.upper()))
    output_html = "<table>{}</table>".format("".join(output_list))
    output = "{}: {}/{} memory modules are healthy. {} without status.\n{}".format(
        state, ok_counter+unknown_counter+warn_counter, component_counter, unknown_counter, output_html)
    return output, exitcode


def mode_thermal(session, args):
    state = "OK"
    exitcode = [0]
    output_list = [
        '<tr><th>Type</th><th>Name</th><th>Health</th></tr>']
    component_counter = 0
    ok_counter = 0
    unknown_counter = 0
    warn_counter = 0
    response = query_api(session, '/Chassis/System.Embedded.1/Thermal', args)
    members = response['Fans'] + \
        response['Redundancy'] + response['Temperatures']

    for r in members:
        status = r['Status']['Health']
        if status != None:
            status = status.lower()
        else:
            status = "Empty"
        if status in ['ok']:
            ok_counter += 1
            color = '#23a34e'
        elif status in [None, 'Empty']:
            color = '#eb7d34'
            unknown_counter += 1
            exitcode.append(ExitCodes.NAGIOS_UNKNOWN.value)
        elif status in ['Warning']:
            color = '#ffa500'
            warn_counter += 1
            exitcode.append(ExitCodes.NAGIOS_WARNING.value)
        else:
            state = "CRITICAL"
            exitcode.append(ExitCodes.NAGIOS_CRITICAL.value)
            color = '#ff5b33'
        component_counter += 1
        output_list.append('<tr><td>{}</td><td>{}</td><td style="background-color:{}">{}</td></tr>'.format(
            r['@odata.type'], r['Name'], color, status.upper()))
    output_html = "<table>{}</table>".format("".join(output_list))
    output = "{}: {}/{} thermal sensors are healthy. {} without status.\n{}".format(
        state, ok_counter+unknown_counter+warn_counter, component_counter, unknown_counter, output_html)
    return output, exitcode


def mode_controller(session, args):
    state = "OK"
    exitcode = [0]
    output_list = [
        '<tr><th>Description</th><th>Name</th><th>Health</th></tr>']
    component_counter = 0
    ok_counter = 0
    unknown_counter = 0
    warn_counter = 0
    response = query_api(
        session, '/Systems/System.Embedded.1/Storage?$expand=*($levels=1)', args)
    members = response['Members']

    for r in members:
        status = r['Status']['HealthRollup']
        if status != None:
            status = status.lower()
        else:
            status = "Empty"
        if status in ['ok']:
            ok_counter += 1
            color = '#23a34e'
        elif status in [None, 'Empty']:
            color = '#eb7d34'
            unknown_counter += 1
            exitcode.append(ExitCodes.NAGIOS_UNKNOWN.value)
        elif status in ['Warning']:
            color = '#ffa500'
            warn_counter += 1
            exitcode.append(ExitCodes.NAGIOS_WARNING.value)
        else:
            state = "CRITICAL"
            exitcode.append(ExitCodes.NAGIOS_CRITICAL.value)
            color = '#ff5b33'
        component_counter += 1
        output_list.append('<tr><td>{}</td><td>{}</td><td style="background-color:{}">{}</td></tr>'.format(
            r['Description'], r['Name'], color, status.upper()))
    output_html = "<table>{}</table>".format("".join(output_list))
    output = "{}: {}/{} controller(s) are healthy. {} without status.\n{}".format(
        state, ok_counter+unknown_counter+warn_counter, component_counter, unknown_counter, output_html)
    return output, exitcode


def mode_dellsystem(session, args):
    state = "OK"
    exitcode = [0]
    output_list = [
        '<tr><th>Component</th><th>Health</th></tr>']
    component_counter = 0
    ok_counter = 0
    unknown_counter = 0
    warn_counter = 0
    response = query_api(
        session, '/Dell/Systems/System.Embedded.1/DellSystem', args)
    members = response['Members']

    for r in members:
        for key in r.keys():
            if r[key] is not None:
                if 'rollupstatus' in key.lower():
                    status = r[key].lower()

                    if status in ['ok']:
                        ok_counter += 1
                        color = '#23a34e'
                    elif status in [None, 'Empty']:
                        color = '#eb7d34'
                        unknown_counter += 1
                        exitcode.append(ExitCodes.NAGIOS_UNKNOWN.value)
                    elif status in ['Warning']:
                        color = '#ffa500'
                        warn_counter += 1
                        exitcode.append(ExitCodes.NAGIOS_WARNING.value)
                    else:
                        state = "CRITICAL"
                        exitcode.append(ExitCodes.NAGIOS_CRITICAL.value)
                        color = '#ff5b33'
                    component_counter += 1
                    output_list.append('<tr><td>{}</td><td style="background-color:{}">{}</td></tr>'.format(
                        key.replace('RollupStatus', ''), color, status.upper()))
    output_html = "<table>{}</table>".format("".join(output_list))
    output = "{}: {}/{} component(s) are healthy. {} without status.\n{}".format(
        state, ok_counter+unknown_counter+warn_counter, component_counter, unknown_counter, output_html)
    return output, exitcode


def mode_health(session, args):
    state = "OK"
    exitcode = [0]
    output_list = [
        '<tr><th>Component</th><th>Category</th><th>Health</th></tr>']
    component_counter = 0
    ok_counter = 0
    unknown_counter = 0
    warn_counter = 0
    response = query_api(
        session, '/Systems/System.Embedded.1/Oem/Dell/DellRollupStatus', args)
    members = response['Members']

    members.sort(key=lambda x: x['RollupStatus'])
    for r in members:
        status = r['RollupStatus'].lower()
        if status in ['ok']:
            ok_counter += 1
            color = '#23a34e'
        elif status in [None, 'Empty']:
            color = '#eb7d34'
            unknown_counter += 1
            exitcode.append(ExitCodes.NAGIOS_UNKNOWN.value)
        elif status in ['Warning']:
            color = '#ffa500'
            warn_counter += 1
            exitcode.append(ExitCodes.NAGIOS_WARNING.value)
        else:
            state = "CRITICAL"
            exitcode.append(ExitCodes.NAGIOS_CRITICAL.value)
            color = '#ff5b33'
        component_counter += 1
        output_list.append('<tr><td>{}</td><td>{}</td><td style="background-color:{}">{}</td></tr>'.format(
            r['InstanceID'], r['SubSystem'], color, status.upper()))
    output_html = "<table>{}</table>".format("".join(output_list))
    output = "{}: {}/{} component(s) are healthy. {} without status.\n{}".format(
        state, ok_counter+unknown_counter+warn_counter, component_counter, unknown_counter, output_html)
    return output, exitcode


def mode_version(session, args):
    exitcode = [0]
    response = query_api(
        session, '/Managers?$expand=*($levels=1)', args)
    member = response['Members'][0]
    output = "OK: iDRAC '{}' reachable. Version '{}' / Model '{}'".format(args.HOSTNAME,
        member['FirmwareVersion'], member['Model'])

    return output, exitcode


def query_api(session, endpoint, args):
    if not endpoint.__contains__(session.default_prefix):
        r = session.get(session.default_prefix+endpoint, None)
    else:
        r = session.get(endpoint, None)
    response = json.loads(r.text)
    if args.DUMPRESPONSE:
        with open("{}_response.json".format(args.MODE), mode='w') as output:
            output.write(r.text)
    if r.status not in [200, 206]:
        raise Exception('API Error {} {}: {}'.format(
            endpoint, r.status, response['error']['@Message.ExtendedInfo'][0]['Message']))
    return response


def logout(session):
    session.logout()


if __name__ == '__main__':
    a = args()

    try:
        session = redfish.redfish_client(base_url=a.HOSTNAME, username=a.USER,
                                         password=a.PASSWORD, default_prefix='/redfish/v1/', timeout=a.TIMEOUT, max_retry=1)
        session.login(auth="session")
        atexit.register(logout, session)
        # Here we dynamically load our function depending on the specified MODE argument
        mode = globals()['mode_{}'.format(a.MODE.replace("-", "_"))]
        output, exitcode = mode(session, a)

        print(output)
        if ExitCodes.NAGIOS_CRITICAL.value in exitcode:
            sys.exit(ExitCodes.NAGIOS_CRITICAL.value)
        elif ExitCodes.NAGIOS_WARNING.value in exitcode:
            sys.exit(ExitCodes.NAGIOS_WARNING.value)
        else:
            sys.exit(ExitCodes.NAGIOS_OK.value)
    except redfish.rest.v1.RetriesExhaustedError as e:
        print("CRITICAL: iDRAC not reachable. / iDRAC: {} / Type: {} / Message: {}".format(a.HOSTNAME,
                                                                                          type(e).__name__, e))
        sys.exit(1)
    except Exception as e:
        if a.MODE == 'version':
            status = 'CRITICAL'
            exitcode = ExitCodes.NAGIOS_CRITICAL.value
        else:
            status = 'UNKNOWN'
            exitcode = ExitCodes.NAGIOS_UNKNOWN.value
        print("{}: An error occured. / iDRAC: {} / Type: {} / Message: {}".format(status, a.HOSTNAME,
                                                                                 type(e).__name__, e))
        sys.exit(exitcode)

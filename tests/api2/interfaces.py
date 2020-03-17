#!/usr/bin/env python3

# Author: Eric Turgeon
# License: BSD

import pytest
import sys
import os
import random

apifolder = os.getcwd()
sys.path.append(apifolder)
from auto_config import interface, ip
from functions import GET, PUT, POST

aliases = {'address': ip}

# Create a random IP
vlan1_ip = f"192.168.0.{random.randint(10, 250)}"


def test_01_get_interface_name():
    results = GET(f'/interface?name={interface}')
    assert results.status_code == 200, results.text
    assert isinstance(results.json(), list) is True, results.text
    print(interface)
    print(results.json())
    assert results.json()[0]["name"] == interface, results.text


def test_02_get_interface_aliases_ip():
    results = GET(f'/interface?name={interface}')
    assert results.status_code == 200, results.text
    assert isinstance(results.json(), list) is True, results.text
    for aliases_list in results.json()[0]['state']['aliases']:
        assert isinstance(aliases_list['address'], str) is True, results.text
        # no break to look all address value are string
        if ip in aliases_list['address']:
            interface_ip = aliases_list['address']
    assert interface_ip == ip, results.text


def test_03_get_interface_aliases_broadcast_ip():
    results = GET(f'/interface?name={interface}')
    assert results.status_code == 200, results.text
    assert isinstance(results.json(), list) is True, results.text
    for aliases_list in results.json()[0]['state']['aliases']:
        if ip in aliases_list['address']:
            broadcast_ip = aliases_list['broadcast']
            break
    assert isinstance(broadcast_ip, str) is True, results.text
    aliases['broadcast'] = broadcast_ip


def test_04_get_interface_aliases_type():
    results = GET(f'/interface?name={interface}')
    assert results.status_code == 200, results.text
    assert isinstance(results.json(), list) is True, results.text
    for aliases_list in results.json()[0]['state']['aliases']:
        assert isinstance(aliases_list['type'], str) is True, results.text
        # no break to look all address value are string
        if ip in aliases_list['address']:
            types = aliases_list['type']
    assert types in ('INET', 'INET6'), results.text
    aliases['type'] = types


def test_05_get_interface_aliases_netmask():
    results = GET(f'/interface?name={interface}')
    assert results.status_code == 200, results.text
    assert isinstance(results.json(), list) is True, results.text
    for aliases_list in results.json()[0]['state']['aliases']:
        if ip in aliases_list['address']:
            netmask = aliases_list['netmask']
            break
    assert isinstance(netmask, int) is True, results.text
    aliases['netmask'] = netmask


def test_06_get_interface_ipv4_in_use():
    global results
    results = POST("/interface/ip_in_use/", {"ipv4": True})
    assert results.status_code == 200, results.text


@pytest.mark.parametrize('dkey', ['type', 'address', 'netmask', 'broadcast'])
def test_07_look_at_interface_ipv4_in_use_output_(dkey):
    assert results.json()[0][dkey] == aliases[dkey], results.text


def test_08_set_main_interface_ipv4_to_false():
    payload = {
        'ipv4_dhcp': False,
        "aliases": [
            {
                'address': ip,
                'netmask': aliases['netmask']
            }
        ]
    }
    results = PUT(f'/interface/id/{interface}/', payload)
    assert results.status_code == 200, results.text
    assert isinstance(results.json(), dict) is True, results.text
    assert results.json()['ipv4_dhcp'] is False, results.text


def test_09_looking_main_interface_ipv4_dhcp_if_is_false():
    results = GET(f'/interface/id/{interface}')
    assert results.status_code == 200, results.text
    assert isinstance(results.json(), dict) is True, results.text
    assert results.json()['ipv4_dhcp'] is False, results.text


@pytest.mark.parametrize('dkey', ['type', 'address', 'netmask'])
def test_10_look_at_interface_aliases_output_(dkey):
    results = GET(f'/interface/id/{interface}')
    assert results.status_code == 200, results.text
    assert isinstance(results.json(), dict) is True, results.text
    assert results.json()['aliases'][0][dkey] == aliases[dkey], results.text


def test_11_creating_vlan1_interface():
    global payload
    payload = {
        "ipv4_dhcp": False,
        "aliases": [
            {
                'address': vlan1_ip,
                'netmask': aliases['netmask']
            }
        ],
        "vlan_parent_interface": interface,
        "name": "vlan1",
        "type": "VLAN",
        "vlan_tag": 1,
        "vlan_pcp": 1
    }
    global results
    results = POST('/interface/', payload)
    assert results.status_code == 200, results.text
    assert isinstance(results.json(), dict) is True, results.text
    global interfaces_id
    interfaces_id = results.json()['id']


@pytest.mark.parametrize('dkey', ["ipv4_dhcp", "name", "vlan_parent_interface",
                                  "type", "vlan_tag", "vlan_pcp"])
def test_12_compare_payload_with_created_vlan1_interface_result_output_(dkey):
    assert results.json()[dkey] == payload[dkey], results.text


def test_13_get_the_vlan1_interface_results():
    global results
    results = GET(f'/interface/id/{interfaces_id}/')
    assert results.status_code == 200, results.text
    assert isinstance(results.json(), dict) is True, results.text


@pytest.mark.parametrize('dkey', ["ipv4_dhcp", "name", "vlan_parent_interface",
                                  "type", "vlan_tag", "vlan_pcp"])
def test_14_compare_payload_with_get_vlan1_interface_result_output_(dkey):
    assert results.json()[dkey] == payload[dkey], results.text


def test_15_get_interface_has_pending_changes():
    results = GET('/interface/has_pending_changes')
    assert results.status_code == 200, results.text
    assert isinstance(results.json(), bool) is True, results.text
    assert results.json() is True, results.text


def test_16_commite_interface():
    payload = {
        "rollback": True,
        "checkin_timeout": 10
    }
    results = POST('/interface/commit/', payload)
    assert results.status_code == 200, results.text


def test_17_get_interface_checkin_waiting():
    results = GET('/interface/checkin_waiting/')
    assert results.status_code == 200, results.text
    assert isinstance(results.json(), float), results.text


def test_18_get_interface_checkin():
    results = GET('/interface/checkin/')
    assert results.status_code == 200, results.text
    assert results.json() is None, results.text


def test_19_get_interface_has_pending_changes():
    results = GET('/interface/has_pending_changes')
    assert results.status_code == 200, results.text
    assert isinstance(results.json(), bool) is True, results.text
    assert results.json() is False, results.text


def test_20_get_the_vlan1_interface_from_id():
    results = GET(f'/interface/id/{interfaces_id}/')
    assert results.status_code == 200, results.text

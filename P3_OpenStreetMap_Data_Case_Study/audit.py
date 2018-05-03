#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xml.etree.cElementTree as ET
from datetime import datetime
from collections import defaultdict
import re
from pprint import pprint

FIELDS = {
    'node': ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp'],
    'node_tags': ['k', 'v'],
    'way': ['id', 'user', 'uid', 'version', 'changeset', 'timestamp'],
    'way_tags': ['k', 'v'],
    'way_nodes': ['ref']
}

MAPDATA = "wuhan.osm"

#-------------------------------------------------------------------------------------------
#-------------------------------- audit ----------------------------------------------------
#-------------------------------------------------------------------------------------------
# 验证 int 类型的变量
def parse_int(s):
    try:
        s = int(str(s).strip())
        return s
    except ValueError:
        return  None

# 验证 float 类型的变量
def parse_float(s):
    try:
        s = float(str(s).strip())
        return s
    except ValueError:
        return None

# 验证 datetime 类型的变量
def parse_datetime(s):
    try:
        s = datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ")
        return s
    except ValueError:
        return None

# 验证变量类型
def detect_type(s):
    if s == 'NULL' or s == '':
        return type(None)
    elif s.startswith('{'):
        return type(list())
    elif parse_int(s) is not None:
        return type(int())
    elif parse_float(s) is not None:
        return type(float())
    elif parse_datetime(s) is not None:
        return type(datetime.now())
    else:
        return type(str())

# 检查 postcode 是否有效
def check_postcode(postcode):
    if parse_int(postcode) is None or len(postcode) != 6 or not postcode.startswith('43'):
        return False
    else:
        return True


def audit(osm_file):
    audit_results = {}
    field_types = {'node': {}, 'node_tags': {}, 'way': {}, 'way_tags': {}, 'way_nodes': {}}
    field_validity = {'node': {}, 'node_tags': {}, 'way': {}, 'way_tags': {}, 'way_nodes': {}}

    name_en_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)
    expected = ['Road', 'Street', 'Expressway', 'Bridge', 'Highway', 'River', 'Lake', "Hutong"
                'Park', 'Zone', 'Area', 'Alley', 'Market', 'Campus', 'Gate', 'Hall', 'Engineering',
                'China', 'Elegance', 'Avenue', 'Mansion', 'Square', 'Palace', 'Hotel', 'Rail',
                'Quarter', "Building", "Line", "Apartment", "Airport", "Institute", "College"]

    # for a given tag, update the set of its field types based on current element
    def update_field_types(e, tag):
        for field in FIELDS[tag]:
            if field not in field_types[tag]:
                field_types[tag][field] = set()
            field_types[tag][field].add(detect_type(e.attrib[field]))

    # 验证时间标记
    def validate_timestamp(e, tag):
        timestamp = parse_datetime(e.attrib['timestamp'])
        if timestamp is not None:
            if timestamp < field_validity[tag]['timestamp'][0]:
                field_validity[tag]['timestamp'][0] = timestamp
            if timestamp > field_validity[tag]['timestamp'][1]:
                field_validity[tag]['timestamp'][1] = timestamp

    # 验证经纬度和时间信息是否有效
    def validate_node(e, tag):
        if field_validity[tag] == {}:
            field_validity[tag] = {
                'lat': [90, 0],
                'lon': [180, -180],
                'timestamp': [datetime.now(), datetime(1970, 1, 1, 0, 0, 0)]
            }

        lat = parse_float(e.attrib['lat'])
        if lat is not None:
            if lat < field_validity[tag]['lat'][0]:
                field_validity[tag]['lat'][0] = lat
            if lat > field_validity[tag]['lat'][1]:
                field_validity[tag]['lat'][1] = lat

        lon = parse_float(e.attrib['lon'])
        if lon is not None:
            if lon < field_validity[tag]['lon'][0]:
                field_validity[tag]['lon'][0] = lon
            if lon > field_validity[tag]['lon'][1]:
                field_validity[tag]['lon'][1] = lon
        validate_timestamp(e, tag)

    # 验证 way 的 timestamp 是否有效
    def validate_way(e, tag):
        if field_validity[tag] == {}:
            field_validity[tag] = {
                'timestamp': [datetime.now(), datetime(1970, 1, 1, 0, 0, 0)]
            }
        validate_timestamp(e, tag)

    # 验证 postcode 格式是否正确
    def validate_postcode(e, tag):
        if e.attrib['k'] == 'addr:postcode':
            postcode = e.attrib['v']
            if not check_postcode(postcode):
                field_validity[tag]['postcode'].add(postcode)


    def validate_node_tags(e, tag):
        if field_validity[tag] == {}:
            field_validity[tag] = {
                'postcode': set()
            }
        validate_postcode(e, tag)

    # 验证 name:en
    def validate_way_name_en(e, tag):
        if e.attrib['k'] == 'name:en':
            name_en = e.attrib['v']
            m = name_en_re.search(name_en)
            if m:
                way_type = m.group()
                if way_type not in expected:
                    field_validity[tag]['name_en'][way_type].add(name_en)
    
    # 验证 way 的 'name_en'、'postcode'
    def validate_way_tags(e, tag):
        if field_validity[tag] == {}:
            field_validity[tag] = {
                'name_en': defaultdict(set),
                'postcode': set()
            }
        validate_way_name_en(e, tag)
        validate_postcode(e, tag)


    for _, ele in ET.iterparse(osm_file):
        if ele.tag == 'node':
            update_field_types(ele, 'node')
            validate_node(ele, 'node')

            for e_tag in ele.iter('tag'):
                update_field_types(e_tag, 'node_tags')
                validate_node_tags(e_tag, 'node_tags')

        if ele.tag == 'way':
            update_field_types(ele, 'way')
            validate_way(ele, 'way')

            for e_tag in ele.iter('tag'):
                update_field_types(e_tag, 'way_tags')
                validate_way_tags(e_tag, 'way_tags')

            for e_nd in ele.iter('nd'):
                update_field_types(e_nd, 'way_nodes')


    audit_results['field_types'] = field_types
    audit_results['field_validity'] = field_validity

    return audit_results


#-------------------------------------------------------------------------------------------
#-------------------------------- cleaning ----------------------------------------------------
#-------------------------------------------------------------------------------------------

mapping = { 
            "jie": "Street",
            "lu": " Road",
            "road": "Road",
            "Bldg": "Building",
            "Ave": "Avenue",
            "Rd": "Road",
            "Lu": "Road",
            "St.": "Street",
            "Str": "Street",
            "Rd.": "Road"
        }

# 将街道名称更新为规范的格式
def update_way_names(name, mapping):
    for k, v in mapping.items():
        if k in name:
            name = name.replace(k, mapping[k])
            return name
    return name


#-------------------------------------------------------------------------------------------
#--------------------------------- test ----------------------------------------------------
#-------------------------------------------------------------------------------------------

def test():
    audit_results = audit(MAPDATA)

    print "Field Types:"
    field_types = audit_results['field_types']
    pprint(field_types)

    assert field_types['node']["lat"] == set([type(float())])
    assert field_types['node']["lon"] == set([type(float())])
    assert field_types['node']["timestamp"] == set([type(datetime.now())])

    assert field_types['node_tags']["k"] == set([type(str())])
    assert field_types['node_tags']["v"] <= set([type(str()), type(int()), type(float()), type(datetime.now())])

    assert field_types['way']["id"] == set([type(int())])
    assert field_types['way']["timestamp"] == set([type(datetime.now())])

    assert field_types['way_tags']["k"] == set([type(str())])
    assert field_types['way_tags']["v"] <= set([type(str()), type(int()), type(float())])

    assert field_types['way_nodes']["ref"] == set([type(int())])

    print "Field Validity:"
    field_validity = audit_results['field_validity']
    pprint(field_validity)

    for st_type, ways in field_validity['way_tags']['name_en'].iteritems():
        for name in ways:
            better_name = update_way_names(name, mapping)
            if name != better_name:
                print name, '->', better_name
            if name == 'Haohu Ave':
                assert better_name == 'Haohu Avenue'
            if name == 'Huang Xiao He Rd':
                assert better_name == 'Huang Xiao He Road'


if __name__ == "__main__":
    test()




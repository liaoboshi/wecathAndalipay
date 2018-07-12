#!/usr/bin/env python
# -*- coding:utf8 -*-

import requests
import json


URL = '''http://kibana.spdb.uline.cc/app/kibana#/discover?_g=()&_a=(columns:!(_source),index:'ul-gw-*',interval:auto,query:(query_string:(analyze_wildcard:!t,query:'*')),sort:!('msg.@timestamp',desc))'''
rs = requests.get(url=URL)
rs.encoding = 'utf-8'


if rs.status_code == 200:

    data = ''''{"index":["ul-gw-*"],"ignore_unavailable":true,"preference":1517998826826}{"version":true,"size":500,"sort":[{"msg.@timestamp":{"order":"desc","unmapped_type":"boolean"}}],"query":{"bool":{"must":[{"query_string":{"query":"*","analyze_wildcard":true}},{"range":{"msg.@timestamp":{"gte":1517997942923,"lte":1517998842923,"format":"epoch_millis"}}}],"must_not":[]}},"_source":{"excludes":[]},"aggs":{"2":{"date_histogram":{"field":"msg.@timestamp","interval":"30s","time_zone":"Asia/Shanghai","min_doc_count":1}}},"stored_fields":["*"],"script_fields":{},"docvalue_fields":["@timestamp","msg.@timestamp"],"highlight":{"pre_tags":["@kibana-highlighted-field@"],"post_tags":["@/kibana-highlighted-field@"],"fields":{"*":{"highlight_query":{"bool":{"must":[{"query_string":{"query":"*","analyze_wildcard":true,"all_fields":true}},{"range":{"msg.@timestamp":{"gte":1517997942923,"lte":1517998842923,"format":"epoch_millis"}}}],"must_not":[]}}}},"fragment_size":2147483647}}'''
    HEADERS = {'Accept':'application/json, text/plain, */*','Accept-Encoding':'gzip, deflate','Accept-Language':'zh-CN,zh;q=0.9,en;q=0.8','Connection':'keep-alive','Content-Length':'969','content-type':'application/x-ndjson','Host':'kibana.spdb.uline.cc','kbn-version':'5.5.1','Origin':'http://kibana.spdb.uline.cc','Referer':'http://kibana.spdb.uline.cc/app/kibana','User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'}
    # HEADERS={'kbn-xsrf':'kbn-version: 5.5.1','kbn-version':'5.5.1'}
    s_order = requests.post(url='http://kibana.spdb.uline.cc/elasticsearch/_msearch',headers=HEADERS,data=json.dumps(data))
    print(s_order.status_code)
    print(s_order.content)
    print(1111)

else:
    print(222)






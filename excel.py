#!/usr/bin/env python
# -*- coding:utf8 -*-

# pyexcel_xls 以 OrderedDict 结构处理数据
from collections import OrderedDict

from pyexcel_xls import get_data
from pyexcel_xls import save_data


# def read_xls_file():
#     xls_data = get_data(unicode(r"D:write_test.xls", "utf-8"))
#     print ("Get data type:", type(xls_data))
#     for sheet_n in xls_data.keys():
#         print (sheet_n, ":", xls_data[sheet_n])
#     return xls_data


# 写Excel数据, xls格式
# def save_xls_file():
#     data = OrderedDict()
#     # sheet表的数据
#     sheet_1 = []
#     row_1_data = [u"商户号", u"密钥"]  # 每一行的数据
#     row_2_data = [4,5]
#     row_3_data = [8,9]
#     # 逐条添加数据
#     sheet_1.append(row_1_data)
#     sheet_1.append(row_2_data)
#     sheet_1.append(row_3_data)
#     # 添加sheet表
#     data.update({u"这是XX表": sheet_1})
#
#     # 保存成xls文件
#     save_data("write_test.xls", data)
#
#
# if __name__ == '__main__':
#     save_xls_file()


# import xlrd
#
# workbook = xlrd.open_workbook('D:\\write_test.xls')
# print(workbook.sheet_names())  # 查看所有sheet
# booksheet = workbook.sheet_by_index(0)  # 用索引取第一个sheet
# booksheet = workbook.sheet_by_name('这是XX表')  # 或用名称取sheet
# # 读单元格数据
# cell_11 = booksheet.cell_value(0, 0)
# cell_21 = booksheet.cell_value(1, 0)
# # 读一行数据
# row_3 = booksheet.row_values(1)
# print(cell_11, cell_21, row_3)


import xlrd

data = xlrd.open_workbook('no_key.xls')

table = data.sheets()[0]

nrows = table.nrows #行数

ncols = table.ncols #列数

for i in range(1,nrows):
    rowValues= table.row_values(i) #某一行数据
    print(rowValues[0],type(rowValues[0]))
    for item in rowValues:
        # print(item)
        pass
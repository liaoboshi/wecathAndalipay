#！/usr/bin/env python
#-*- conding:utf-8 -*-


class Diy_page(object):
    def __init__(self,total_count,current_page,per_page_num,
                 max_page_num,index_url):
        # 数据源总记录条数
        self.total_count = total_count
        # 接收用户发送的当前页码
        try:
            v = int(current_page)
            if v<=0:  #如果用户输入的页码小于1，直接让它等于1
                v = 1
            self.current_page = v
        except Exception as  e:
            self.current_page = 1
        # 每一页显示的记录条数
        self.per_page_num = per_page_num
        # 每一页显示的最多页码数
        self.max_page_num = max_page_num
        self.index_url = index_url
    @property
    def num_pages(self):
        '''
        总页码数
        :return:
        '''
        a,b = divmod(self.total_count,self.per_page_num)
        if b == 0:
            return a
        else:
            return a+1
    def page_range(self):
        '''
        每一页所能显示的最多页码数范围
        :return:
        '''
        if self.num_pages<self.max_page_num:  #如果总页码小于每一页显示的最多页码总数
            return range(1,self.num_pages+1)
        part = int(self.max_page_num/2)
        if self.current_page <= part:  #如果当前页小于等于每页显示最多页码数的一半
            return range(1,self.max_page_num+1)
        if self.current_page+part>self.num_pages:   #如果当前页加每页显示最多页码数的一半大于总页码数
            return range(self.num_pages-self.max_page_num,self.num_pages+1)
        return range(self.current_page-part,self.current_page+part+1)
    def start_page(self):
        '''
        切片的起始位置
        :return:
        '''
        return (self.current_page-1)*self.per_page_num
    def end_page(self):
        '''
        切片的结束位置
        :return:
        '''
        return self.current_page*self.per_page_num
    def a_num_pages(self):
        '''
        每一页底部页码链接标签
        :return:
        '''
        li = []
        head_page = "<li><a href='%s?p=1'>首页</a></li>"%(self.index_url)
        li.append(head_page)
        if self.current_page ==1:
            prev_page = "<li><a href='#'>上一页</a></li>"   #生成上一页标签
        else:
            prev_page = "<li><a href='%s?p=%s'>上一页</a></li>"%(self.index_url,self.current_page-1)
        li.append(prev_page)
        for row in self.page_range():
            if row == self.current_page:
                data = "<li class='active'><a href='%s?p=%s'>%s</a></li>"%(self.index_url,row,row)
            else:
                data = "<li><a href='%s?p=%s'>%s</a></li>" % (self.index_url,row, row)
            li.append(data)
        if self.current_page ==self.num_pages:
            next_page = "<li><a href='#'>下一页</a></li>"  #生成下一页标签
        else:
            next_page = "<li><a href='%s?p=%s'>下一页</a><li>"%(self.index_url,self.current_page+1)
        li.append(next_page)
        # last_page = "<li><a href='%s?p=%s'>尾页</a><li><form action='%s' method='get'><input type='text' name='p'><input type='submit'></form>"%(self.index_url,self.num_pages,self.index_url)
        last_page = "<li><form style='display:inline; action='' method='get'><input style='width:40px;' type='text' name='p'><input type='submit'></form><li><li><a href='%s?p=%s'>尾页</a><li>"%(self.num_pages,self.index_url)
        li.append(last_page)
        return "".join(li)



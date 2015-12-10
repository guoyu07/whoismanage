#!/usr/bin/python
# encoding:utf-8
"""
网站后台定期更新程序
功能：更新表domain_summary,domain_update两个表。

"""
import sys
from database import conn_db
import time
import threading
from threading import Thread
from Queue import Queue
import MySQLdb


num_thread = 5      # 线程数量
queue = Queue()     # 任务队列，存储sql
sum_domains = []    # 存储域名的和
lock = threading.Lock()

def sum_all_domains(sum_domains=[], single_domains=[]):
    """合并两个列表，相同名称求和"""

    del_index = []      # 用来存放待删除的index
    for index_sum, value_sum in enumerate(sum_domains):
        for index_single, value_single in enumerate(single_domains):
            if value_sum[0] == value_single[0]:
                sum_domains.append(
                    (value_sum[0], value_single[1] + value_sum[1]))
                del_index.append(index_sum)
                del single_domains[index_single]  # 删除

    sum_domains.extend(single_domains)  # 将次列表中未删除的添加
    del_index.reverse()  # 反向求解,比较巧妙,防止删除前面项后，导致错位
    for i in del_index:  # 删除重复的项
        del sum_domains[i]


def count_domain(q, queue):
    """计算各个列表中，各个顶级后缀的数量，并求和"""
    while 1:
        content = queue.get()
        if not content:
            queue.task_done()
            # break
        try:
            print "线程：" + str(q) + "探测各个域名顶级后缀的域名数量..."
            conn = conn_db()
            cur = conn.cursor()
            cur.execute(content)
            single_domains = cur.fetchall()
            lock.acquire()  # 锁
            sum_all_domains(sum_domains, list(single_domains))
            lock.release()  # 解锁
            queue.task_done()
            time.sleep(1)  # 去掉偶尔会出现错误
        except MySQLdb.Error, e:
            print "Error %d: %s" % (e.args[0], e.args[1])
            sys.exit(1)
        finally:
            print "线程: "+str(q)+" 探测结束"
            cur.close()
            conn.close()


def update_db():    
    """更新数据库"""
    conn = conn_db()
    sql = 'INSERT INTO domain_update(tld_name, domain_num) VALUES(%s, %s)'
    cur = conn.cursor()
    for domain in sum_domains:
        cur.execute(sql, (domain[0], domain[1]))
    conn.commit()
    cur.execute('TRUNCATE TABLE domain_summary')
    sql = 'INSERT INTO domain_summary(tld_name, domain_num) VALUES(%s, %s)'
    for domain in sum_domains:
        cur.execute(sql, (domain[0], domain[1]))
    conn.commit()
    cur.close()
    conn.close()

def create_queue():
    """
    创建任务队列
    """
    for i in xrange(65, 91):     # 创建任务队列，A-Z
        sql = 'SELECT SUBSTRING_INDEX(domain,".",-1) as tld, count(*) AS count \
               FROM domain_whois_%s  GROUP BY tld' % chr(i)
        queue.put(sql)
    sql_num = 'SELECT SUBSTRING_INDEX(domain,".",-1) as tld, count(*) AS count \
                FROM domain_whois_num GROUP BY tld'
    queue.put(sql_num)  # domain_whois_num 加入队列
    sql_other = 'SELECT SUBSTRING_INDEX(domain,".",-1) as tld, count(*) AS count \
                FROM domain_whois_other GROUP BY tld'
    queue.put(sql_other)  # domain_whois_other 加入队列
    
def create_thread():
    for q in range(num_thread):  # 开始任务
        worker = Thread(target=count_domain, args=(q, queue))
        worker.setDaemon(True)
        worker.start()
    queue.join()

def tld_domain():
    """主操作"""
    global sum_domains  
    sum_domains = [] # 务必添加，初始化，否则会一直累加
    create_queue()
    create_thread()
    update_db()
    

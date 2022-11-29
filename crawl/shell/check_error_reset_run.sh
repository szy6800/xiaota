#!/usr/bin/env bash
# 定时恢复连续失败次数小于20,状态为失败的,重新采集, 失败次数大于20的人工介入

/root/XIAO_TA/python_env/xitaEnv/bin/python3  <<-EOF
sql = '''UPDATE tb_site set state=10 where state=19 and fail_times <= 20;'''
import psycopg2
con = psycopg2.connect(
	password='postgres',
	host='192.168.1.203',
	user='postgres',
	database='analysis_crawl',
)
cur = con.cursor()
try:
    cur.execute(sql)
    con.commit()
    print('修改成功')
except Exception as ex:
    print(ex)
finally:
    cur.close()
    con.close()
EOF



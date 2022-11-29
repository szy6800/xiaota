#!/usr/bin/env bash
source /etc/profile;

cd /root/XIAO_TA/crawl/

for i in {1..5}
do
        num=`ps -ef|grep crawl_work.py|grep -v grep|grep -v check|wc -l`
        echo `date` "num=" $num
        if [ $num -lt 40 ]
        then
                echo "start crawl"
		nohup  /usr/bin/python3 crawl_work.py crawl.conf &>/dev/null &
                sleep 1
        else
                break
        fi
done


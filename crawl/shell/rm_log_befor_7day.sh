#!/usr/bin/env bash
# 删除七天前的日志文件
CURRENT_DIR=$(cd "$(dirname "$0")"; cd ../log; pwd)
cd $CURRENT_DIR
find . -name "crawl*.log" -atime +7 -exec rm -f {} \;



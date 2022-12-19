import re
a = '''...</span><a class="page_a page_num" href="/topic/3962147-540-12.html">46</a>
'''


# ls = re.findall(r'<a href="http:\/\/ndcqjy.com\/cn\/cjgg/cgcjgg\/(\d+)">末页',a)
ls = re.findall(r'...</span><a class="page_a page_num" href="/topic/.*">(\d+)</a>',a)
print(ls)







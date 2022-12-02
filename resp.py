import re
a = '''
<li><a href="/zhujianz/listbn4.html" title="跳转到第4页">4</a></li>
'''


# ls = re.findall(r'<a href="http:\/\/ndcqjy.com\/cn\/cjgg/cgcjgg\/(\d+)">末页',a)
ls = re.findall(r'<li><a href="/zhujianz/listbn4.html" title="跳转到第4页">(\d+)</a></li>',a)


print(ls)


# a = '/art/2016/11/18/art_9468_631901.html'
# res = a.split('rt/')[1].split('/a')[0].replace('/','-')
# print(res)
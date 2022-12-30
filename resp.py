import re



def r():
    print('1e1232')


a = ''

# ls = re.findall(r'<a href="http:\/\/ndcqjy.com\/cn\/cjgg/cgcjgg\/(\d+)">末页',a)
ls = re.findall(
    r'<a href="http://www.zgdczb.com/invest/gongcheng/(\d+).html">&nbsp;1333&nbsp;</a>  <a href="http://www.zgdczb.com/invest/gongcheng/2.html">&nbsp;下一页',
    a)
print(ls)



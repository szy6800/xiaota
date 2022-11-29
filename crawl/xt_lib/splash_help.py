# -*- coding: utf-8 -*-
# !/usr/bin/env python
# Software: PyCharm
# __author__ == "YU HAIPENG"
# fileName: splash_help.py
# Month: 九月
# time: 2020/9/16 19:08
# noqa
""" Whttps://splash-cn-doc.readthedocs.io/zh_CN/latest/faq.html """
import requests
from requests.utils import requote_uri
from urllib.parse import urlencode, quote
import json

User_Agent = "Mozilla/5.0 (Windows NT 4.0; WOW64) AppleWebKit/537.36 " \
             "(KHTML, like Gecko) Chrome/37.0.2049.0 Safari/537.36"


class SplashHelp(object):
    """
    splash.args
        是一个传入参数的table类型，它包含了来自GET请求的原始url的合并值和数据类型为application/json 的POST请求的请求体的值
        例如您在使用 Splash HTTP API的时候在脚本的参数中添加了一个url参数，那么 splash.args.url 就包含了您传入的这个URL [10]

    function main(splash, args)

        splash.js_enabled = true/false
            允许或者禁止执行嵌入到页面中的JavaScript代码 默认情况下允许执行JavaScript代码

        splash.private_mode_enabled = true/false
            默认情况下匿名模式是开启的

        splash.resource_timeout = number   # splash.resource_timeout=10
            当请求远端的资源超过10s时异常告警当值为0或者nil时表示没有设置超时值
            在设置请求的超时值事，在 splash:on_request 函数中使用 request:set_timeout
            设置的超时值要优先于 splash.resource_timeout
            永远在代码中设置 resource_timeout 是一个很好的做法，大部分情况下可以设置

        splash.images_enabled = true/false
            禁止加载图片能节省大量的网络带宽(通常在50%左右)并且能提高渲染的速度。
            请注意这个选项可能会影响页面中JavaScript代码 的执行：禁止加载图片可能会影响DOM元素的坐标或者大小，
            而在脚本中可能会读取并使用它们

         splash.plugins_enabled = true/false
            允许或者禁止浏览器插件(例如 Falsh) 默认情况下插件是被禁止的

         splash.response_body_enabled = true/false  从效率上考虑，默认情况下Splash不会在内存中保存每个请求的响应内容。
            这就意味着在函数 splash:on_response 的回调函数中，我们无法获取到 response.body 属性，
            同时也无法从 HAR 中获取到响应的对应内容。可以通过在lua脚本中设置 splash.response_body_enabled = true
            来使响应内容变得有效
            请注意，不管 splash.response_body_enabled 是否设置，
            在:ref:splash:http_get <splash-http-get> 和 splash:http_post
            中总是能获取到 response.body 的内容
            您可以通过在函数 splash:on_request 的回调中设置 request:enable_response_body 来启用每个请求的响应内容跟踪

        splash.scroll_position = {x=..., y=...} 设置或者获取当前滚动的位置 当然，
            您也可以省略您不想改变的坐标值，例如 splash.scroll_position = {y=200} 是将y的值改为200，而x的值保持不变


        assert(splash:go(args.url))
        return {png=splash:png()}
    end

    """

    def __init__(self, splash_base_url: str = ''):
        self.base_url = splash_base_url or "http://localhost:8050/"

    def _send(self, url, method="GET", **kwargs):
        header = kwargs.pop('headers', {})
        session = kwargs.pop('session', None) or requests
        timeout = kwargs.pop('timeout', 30)
        headers = self.update_headers(header)
        request_func = getattr(session, method.lower())
        response = request_func(url, headers=headers, timeout=timeout, **kwargs)
        return response

    def __url_parse(self, uri, params, method, suffix, kwargs):
        """
        spl_default_flag bool
        目标 uri 发post 目前还没有解决
        """
        spl_default_flag = kwargs.pop("spl_default_flag", True)
        splash_params = kwargs.pop("splash_params", None)
        default_spl_params = dict()
        if spl_default_flag:
            default_spl_params.update({"image": 0, "wait": 1, "http_method": "GET"})
        if splash_params is not None:
            default_spl_params.update(splash_params)
        if params is not None:
            if '?' in uri:
                uri = f"{uri.rstrip('&')}&{urlencode(params)}"
            else:
                uri = f"{uri.rstrip('?')}?{urlencode(params)}"
        if "http_method" in default_spl_params:
            default_spl_params['http_method'] = default_spl_params['http_method'].upper()
        if method.upper() == "GET":
            splash_url = f"{self.base_url}{suffix}?url={quote(requote_uri(uri))}&{urlencode(default_spl_params)}"
        else:
            splash_url = f"{self.base_url}{suffix}"
            if "headers" not in default_spl_params:
                default_spl_params["headers"] = [("User-Agent", User_Agent)]
            default_spl_params['url'] = uri
            data = json.dumps(default_spl_params)
            headers = {'Content-Type': 'application/json'}
            kwargs['headers'] = headers
            kwargs['data'] = data
        return splash_url

    def render_html(self, uri, params: dict = None, method="GET", session=None, **kwargs):
        """
        此接口用于获取 html 的渲染后的页面
        params 目标 url 参数
        splash_params: 默认 dict {"image": 0, "wait": 1}
            --params
                timeout -> float : optional 渲染的超时值，以秒为单位(默认为30s)
                resource_timeout -> float : optional 单个网络请求的超时时间
                wait -> float : optional 当收到响应包后等待的时长，单位为s默认为0，如果您所请求的页面中包含一些异步与延时加载
                    的JavaScript脚本时请添加上这个值
                proxy -> string : optional [protocol://][user:password@]proxyhost[:port])
                    其中protocol 为 http或者socks5,如果未指定端口，将会默认采用1080 端口
                js -> string : optional
                js_source -> string : optional  可被页面环境执行的JavaScript代码
                filters -> string : optional 使用分号分隔的请求过滤的名称列表
                allowed_domains -> string : optional 使用分号分隔的允许访问的域名列表。如果该值存在，
                    Splash将不会加载任何来自不在此列表中的域以及不在此列表中的域的子域的任何内容。
                images -> 是否加载图片，当值为1时表示允许加载图片，为0时表示禁止加载
                headers -> JSON array or object : optional 为首个发出去的http请求包设置请求头
                    这个参数仅仅在 application/json 类型的POST包中使用，
                    它可以是使用(header_name, header_value)这种格式的数据组成的json对象，
                    其中header_name表示请求头某项的键，header_value表示请求头某项的值
                    其中“User-Agent”这个头比较特殊，它作用在所有请求包上而不仅仅是首个包
                http_method -> string : optional 传出的Splash包的请求方法 [14] ，默认的方法是GET，当然Splash也支持POST。

        """
        splash_url = self.__url_parse(uri, params, method, "render.html", kwargs)
        return self._send(splash_url, method=method, session=session, **kwargs)

    def render_png(self, uri, params: dict = None, method="GET", session=None, **kwargs):
        """
        此接口用于获取网页截图
        param splash_params:
            它的许多参数都与render.html的相同, 相比较于前者它多出来下面几个参数

            width -> integer : optional 将生成图片宽度调整为指定宽度，以保持宽高比 1200

            height -> integer : optional 将生成的图片裁剪到指定的高度，
                通常与width参数一起使用以生成固定大小的图片 1080

            render_all -> 它可能的值有0和1，表示在渲染前扩展视口以容纳整个Web 页面(即使整个页面很长)，默认值为 render_all=0
                    render_all = 1 时需要一个不为0 的 wait值，这是一个不幸的限制，
                    但是目前来看只能通过这种方式使得在 render_all = 1 这种情况下整个渲染变得可靠
            scale_method -> string : optional 可能的值有 raster (默认值) 和 vector,
                如果值为 raster, 通过宽度执行的缩放操作是逐像素的，如果值为vector, 在缩放是是按照 元素在进行的
            example:
                'http://localhost:8050/render.png?url=http://domain.com/page-with-javascript.html&timeout=10'

                # 将生成图片尺寸设置为:320x240
                'http://localhost:8050/render.png?url=http://domain.com/page-with-javascript.html&width=320&height=240'
        """
        splash_url = self.__url_parse(uri, params, method, "render.png", kwargs)
        return self._send(splash_url, method=method, session=session, **kwargs)

    def render_jpeg(self, uri, params: dict = None, method="GET", session=None, **kwargs):
        """
        param splash_params:
            它的参数与render.png大致相同，相比于前者，它多出一个参数
            quality : integer : optional 该参数表示生成图片的质量，大小在0~100之前，默认值为 75
            example:
                # 生成默认质量的图片
                http://localhost:8050/render.jpeg?url=http://domain.com/

                # 生成高质量的图片
                http://localhost:8050/render.jpeg?url=http://domain.com/&quality=30
        """
        splash_url = self.__url_parse(uri, params, method, "render.jpeg", kwargs)
        return self._send(splash_url, method=method, session=session, **kwargs)

    def render_json(self, uri, params: dict = None, method="GET", session=None, **kwargs):
        """
        与 render.jpeg的参数相似，多余的参数如下:
        param splash_params:
            html : integer : optional
                返回值中是否包含HTML，1为包含，0表示不包含，默认为0
            png : integer : optional
                返回值中是否包含PNG图片，1为包含，0表示不包含，默认为0
            jpeg : integer : optional
                返回值中是否包含JPEG图片，1为包含，0表示不包含，默认为0
            iframes : integer : optional
                返回值中是否包含子frame的信息，1为包含，0表示不包含，默认为0
            script : integer : optional
                是否在返回中包含执行的javascript final语句的结果
                （请参阅：在页面上下文中执行用户自定义的JavaScript代码），
                可选择的值有1（包含） 0（不包含），默认是0
            history : integer : optional
                返回值中是否包含主页面的历史请求/响应数据，可选择的值有1（包含）0（不包含），默认是0
                使用该参数来获取HTTP响应码和对应的头信息，它只会返回最主要的请求/响应信息
                （也就是说页面加载的资源信息和对应请求的AJAX信息是不会返回的）
                要获取请求和响应的更详细信息请使用 har参数

            har : integer : optional
                是否在返回中包含 HAR信息，可选择的值有1（包含）0（不包含），
                默认是0，如果这个选项被打开，那么它将会在har键中返回与render.har 一样的数据

                默认情况下响应体未包含在返回中，如果要返回响应体，可以使用参数 response_body

            response_body : int : optional
                可选择的值有1（包含）0（不包含），如果值为1，
                那么将会在返回的HAR信息中包含响应体的内容。在参数har 和 history为0的情况下该参数无效
            示例:
                默认情况下，返回当前页面的url，请求url，页面标题，主frame的尺寸 [16]
                {
                    "url": "http://crawlera.com/",
                    "geometry": [0, 0, 640, 480],
                    "requestedUrl": "http://crawlera.com/",
                    "title": "Crawlera"
                }
                设置参数 html=1 ，以便让HTML能够加入到返回值中
                {
                    "url": "http://crawlera.com/",
                    "geometry": [0, 0, 640, 480],
                    "requestedUrl": "http://crawlera.com/",
                    "html": "<!DOCTYPE html><!--[if IE 8]>....",
                    "title": "Crawlera"
                }
                设置参数 png=1 以便使渲染后的截图数据以base64的编码方式加入到返回值中
                {
                    "url": "http://crawlera.com/",
                    "geometry": [0, 0, 640, 480],
                    "requestedUrl": "http://crawlera.com/",
                    "png": "iVBORw0KGgoAAAAN...",
                    "title": "Crawlera"
                }
                同时设置html=1和png=1，能同时获取到截图和HTML代码。这样就保证了截图与HTML相匹配

                通过添加 iframes=1，能够在返回中得到对应的frame的信息
                同时设置iframe=1和html=1,以获取所有iframe和HTML（包括iframe的HTML代码）
                {
                        "geometry": [0, 0, 640, 480],
                        "frameName": "",
                        "html": "<!DOCTYPE html...",
                        "title": "Scrapinghub | Autoscraping",
                        "url": "http://scrapinghub.com/autoscraping.html",
                        "childFrames": [
                            {
                                "title": "Tutorial: Scrapinghub's autoscraping tool - YouTube",
                                "url": "",
                                "html": "<!DOCTYPE html>...",
                                "geometry": [235, 502, 497, 310],
                                "frameName": "<!--framePath //<!--frame0-->-->",
                                "requestedUrl": "http://xxx/",
                                "childFrames": []
                            }
                        ],
                        "requestedUrl": "http://scrapinghub.com/autoscraping.html"
                    }
                    请注意，iframe可以嵌套
        """
        splash_url = self.__url_parse(uri, params, method, "render.json", kwargs)
        return self._send(splash_url, method=method, session=session, **kwargs)

    def execute(self, lua_source: str = None, **kwargs):
        """
        最为强大的脚本
        此接口可以实现lua的对接
        example:
            function main(splash)
                local url="{url}"
                splash:set_user_agent("Mozilla/5.0  Chrome/69.0.3497.100 Safari/537.36")
                splash:go(url)
                splash:wait(2)
                splash:go(url)
                return {
                    html = splash:html()
                }
            end
        执行自定义的渲染脚本并返回对应的结果

render.html, render.png, render.jpeg, render.har 和 render.json已经涵盖了许多常见的情形，但是在某些时候这些仍然不够， 这个端口允许用户编写自定义的脚本

        参数:

        lua_source : string : required
        需要浏览器执行的脚本代码，请查看 Splash脚本教程 以获取更多信息
        timeout : float : optional
        与render.html中的timeout参数含义相同
        allowed_domains : string : optional
        与render.html中的allowed_domains参数含义相同
        proxy : string : optional
        与render.html中的proxy参数含义相同
        filters : string : optional
        与render.html中的filters参数含义相同
        save_args : json对象或者是以分号分隔的字符串 : optional
        与render.html中的save_args参数相同，请注意你不仅能保存Splash中的默认参数，也可以保存其他任何参数
        load_args : JSON object or a string : optional
        与render.html中的load_args参数相同，请注意你不仅能加载Splash中的默认参数，也可以加载其他任何参数
        您可以传入任何类型的参数，所有在端点execute中传入的参数在脚本中都可以通过splash.args这个table对象 来访问
        """

        params = 'lua_source={lua_source}'.format(lua_source=quote(lua_source))
        splash_url = f"{self.base_url}execute?{params}"
        return self._send(splash_url, method='get', **kwargs)

    def run(self, lua_source, url, **kwargs):
        """
        这个端点与execute具有相同的功能，但是它会自动将 lua_source 包装在
        function main(splash, args) ... end 结构中 比如您在

        example:
            import requests

                script = '''
                splash:go(args.url)
                return splash:png()
            resp = requests.post('http://localhost:8050/run', json={
                'lua_source': script,
                'url': 'http://example.com'
            })
            png_data = resp.content
        """
        data = {
            "lua_source": lua_source,
            'url': url
        }
        data.update(kwargs)
        splash_url = f"{self.base_url}run"
        session = kwargs.pop("session", None)
        headers = kwargs.pop("headers", {})
        headers.update({'Content-Type': 'application/json'})
        return self._send(
            splash_url,
            json=data, method='post',
            session=session,
            headers=headers
        )

    @staticmethod
    def param_parse(url, separator='&', plus=False):
        """
        :url参数反解字典
        :param url:
        :param plus:
        :param separator: url的分隔符
        :return:
        """

        if plus:
            from urllib.parse import unquote_plus as unquote
        else:
            from urllib.parse import unquote
        temp = dict()
        if url.find('?') != -1:
            param = url.split('?')[1]
        else:
            param = url.split('?')[0]
        param = param.split(separator)
        for i in param:
            if not i:
                continue
            if i.find('=') != -1:
                a, b = i.split('=')
                if a:
                    if isinstance(temp.get(unquote(a)), list):
                        temp[unquote(a)].append(unquote(b))
                    elif temp.get(unquote(a), None) is not None:
                        temp[unquote(a)] = [temp[unquote(a)], unquote(b)]
                    else:
                        temp[unquote(a)] = unquote(b)
        return temp

    @staticmethod
    def update_headers(headers):
        default_headers = {
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Accept": "*/*",
            "User-Agent": User_Agent,
        }
        default_headers.update(headers)
        return default_headers

    def add_cookies_string(self, cookies) -> str:
        cookie_string = ''
        if not cookies:
            return ''
        for cookie in cookies:
            cookie_string += 'splash:add_cookie{"%s", "%s", "%s", domain="%s"}\n' % (
                cookie['name'], cookie['value'], cookie['path'], cookie['domain']
            )
        return cookie_string


if __name__ == '__main__':
    splash = SplashHelp(splash_base_url="http://192.168.1.241:8050/")
    response = splash.render_html('http://httpbin.org/get', method='post')
    spl_params = {
        'html': 1,
        "iframes": 1
    }
    print(response.text)
    # response = splash.render_jpeg('https://www.baidu.com',
    # splash_params=spl_params, spl_default_flag=True)
    # res = splash.render_json('https://www.baidu.com', splash_params=spl_params)
    # print(res.text)

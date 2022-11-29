import httpx

r = httpx.get('https://httpbin.org/get')
print(r)  # <Response [200 OK]>

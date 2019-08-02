# Scrapper

Scrapper is a simple service to fetch webpages. It exposes two endpoints:
* `/pages` - POSTing here will queue fetching task. If successful, you'll get _202 Accepted_ response from service with Location header containing URL for a temporary resource (`/tasks`) providing information about queued task. GET `/pages/{id}` when queued task is completed to see webpage contents.
* `/tasks/{id}` - GET information about background task. If background task is completed successfully, you'll get 303 See Other with redirect to `/pages/{id}` to see actual results.

Scrapper requires MongoDB to work.

### Installation
```
git clone https://github.com/jacek-jablonski/scrapper.git
cd scrapper
make docker-build
```

### Usage
```
make docker-run
```
Service is listening on `http://localhost:8080/`.

1. Request fetching:
<pre>
 ❯ curl -i -d '{"url": "http://github.com"}' -H "Content-Type: application/json" -X POST http://localhost:8080/pages
HTTP/1.1 202 Accepted
<b>Location: /tasks/e8dc0719-ad93-4ac5-8466-7858169509d6</b>
Content-Type: text/plain; charset=utf-8
Content-Length: 13
Date: Fri, 02 Aug 2019 17:44:09 GMT
Server: Python/3.7 aiohttp/3.5.4

202: Accepted
</pre>

2. Get task status:
<pre>
 ❯ curl -iL -H "Content-Type: application/json" -X GET http://localhost:8080/tasks/e8dc0719-ad93-4ac5-8466-7858169509d6
HTTP/1.1 200 OK
Content-Type: application/json; charset=utf-8
Content-Length: 163
Date: Fri, 02 Aug 2019 17:44:10 GMT
Server: Python/3.7 aiohttp/3.5.4

{
  "_id": "8a51f5d7-053e-4587-9893-11d8a0597eb8",
  "created_at": "2019-08-02T17:44:09.506322Z",
  "url": "https://httpstat.us/200?sleep=50000",
  "status": "fetching",
  "error_message": null
}
</pre>

3. When finished - get fetching result:
<pre>
 ❯ curl -iL -H "Content-Type: application/json" -X GET http://localhost:8080/tasks/e8dc0719-ad93-4ac5-8466-7858169509d6
HTTP/1.1 303 See Other
Content-Type: text/plain; charset=utf-8
<b>Location: /pages/06f7f4c8-5771-428b-8e8e-0d46a59f2d81</b>
Content-Length: 14
Date: Fri, 02 Aug 2019 17:44:20 GMT
Server: Python/3.7 aiohttp/3.5.4

HTTP/1.1 200 OK
Content-Type: application/json; charset=utf-8
Content-Length: 92124
Date: Fri, 02 Aug 2019 17:44:20 GMT
Server: Python/3.7 aiohttp/3.5.4

{
    "_id": "06f7f4c8-5771-428b-8e8e-0d46a59f2d81",
    "created_at": "2019-08-02T17:44:10.188744Z",
    "url": "http://github.com",
    "body": <i>cut</i>
}
</pre>

### Additional business rules
If you would like to modify body, you need to provide inherited `Processor` class with one requried `process` method. Uncomment line
```python
app.add_processor(UpperizationProcessor())
```
in `scrapper/main.py` to see how it works. 

### Tests
```
make devinstall
make tests
```
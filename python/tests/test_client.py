import asyncio
import base64
import hashlib
import hmac
import importlib
import inspect
import json
from pathlib import Path
import tempfile
import threading
import time
import typing
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit, parse_qs
import httpx
from classive import (Classive, AsyncClassive, AuthenticationError, InsufficientCreditsError, ConflictError, RateLimitError,
    ServiceError, NetworkError, TimeoutError, ValidationError, ProtocolError, JobFailedError, JobCancelledError, verify_webhook, types)

ROOT = Path(__file__).resolve().parents[2]
INPUT = {"type": "lesson", "prompt": "Teach adding fractions with unlike denominators.", "audience": {"band": "primary"}, "outputs": ["notes"]}
def job(status="completed"):
    return {"id": "job_" + "a" * 20, "object": "job", "type": "lesson", "status": status, "input": INPUT,
            "createdAt": "2026-10-12T00:00:00Z", "startedAt": None, "completedAt": None, "estimatedCompletionAt": None,
            "credits": {"reserved": 0, "charged": 10}, "results": {"lessons": [{"order": 1, "title": "Fractions",
            "notes": {"markdown": None, "pdf": None, "json": {"id": "file_" + "a" * 20,
            "url": "https://api.classive.app/v1/files/file_" + "a" * 20, "bytes": 21, "contentType": "application/json"}}}]}}

class Fixture:
    def __init__(self, handler):
        self.calls = []
        fixture = self
        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args): pass
            def handle_call(self):
                data = self.rfile.read(int(self.headers.get("content-length", 0)))
                call = {"method": self.command, "url": urlsplit(self.path), "headers": dict(self.headers),
                        "body": json.loads(data) if data else None}
                fixture.calls.append(call)
                try:
                    status, body, headers = handler(call)
                    encoded = body if isinstance(body, bytes) else json.dumps(body).encode()
                    self.send_response(status)
                    self.send_header("content-type", "application/json")
                    self.send_header("content-length", str(len(encoded)))
                    for k,v in headers.items(): self.send_header(k, v)
                    self.end_headers()
                    self.wfile.write(encoded)
                except (BrokenPipeError, ConnectionResetError): pass
            do_GET = do_POST = do_PATCH = do_DELETE = handle_call
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.url = f"http://127.0.0.1:{self.server.server_port}"
    def __enter__(self): return self
    def __exit__(self, *args):
        self.server.shutdown(); self.server.server_close(); self.thread.join()

def ok(data): return (200, data, {})

class SyncTests(unittest.TestCase):
    def test_all_52_operations_over_http(self):
        spec = json.loads((ROOT / "schema/openapi.json").read_text())
        ops = json.loads((ROOT / "schema/operations.json").read_text())
        with Fixture(lambda c: ok({"ok": True})) as f, Classive("ck_live_test", base_url=f.url, max_retries=0) as client:
            self.assertEqual(len(ops), 52)
            for op in ops:
                schema = spec["paths"][op["path"]][op["method"].lower()]
                self.assertEqual(schema["operationId"], op["operationId"])
                params = schema.get("parameters", [])
                args = ["file_test" if p["name"] == "fileId" else "id_test" for p in params if p["in"] == "path"]
                body = {"marker": op["operationId"]} if "application/json" in schema.get("requestBody", {}).get("content", {}) else None
                if body is not None: args.append(body)
                query = {p["name"]: True if p["schema"].get("type") == "boolean" else 2 if p["name"] == "limit" else "value" for p in params if p["in"] == "query"}
                kwargs = {"options": {"idempotency_key": "sdk-test"}}
                if query: kwargs["query"] = query
                getattr(getattr(client, op["resource"]), op["python"])(*args, **kwargs)
                call = f.calls[-1]
                self.assertEqual(call["method"], op["method"])
                self.assertEqual(call["url"].path, op["path"].replace("{fileId}", "file_test").replace("{id}", "id_test"))
                self.assertEqual(parse_qs(call["url"].query), {k: [str(v).lower() if isinstance(v,bool) else str(v)] for k,v in query.items()})
                self.assertEqual(call["body"], body)
                self.assertEqual(call["headers"]["Authorization"], "Bearer ck_live_test")
                self.assertEqual(call["headers"]["Idempotency-Key"], "sdk-test")

    def test_quote_create_wait_download(self):
        reads = 0
        def handle(c):
            nonlocal reads
            if c["url"].path == "/v1/jobs/quote":
                self.assertEqual(c["body"], INPUT); return ok({"id": "quo_test", "credits": 10})
            if c["method"] == "POST":
                self.assertEqual(c["body"]["quoteId"], "quo_test")
                self.assertEqual(c["headers"]["Idempotency-Key"], "lesson-1")
                return 201, job("queued"), {}
            if c["url"].path.startswith("/v1/files"): return ok({"title": "Fractions"})
            reads += 1; return ok(job("processing" if reads == 1 else "completed"))
        with Fixture(handle) as f, Classive("test", base_url=f.url) as c, tempfile.TemporaryDirectory() as directory:
            quote = c.jobs.quote(INPUT)
            accepted = c.jobs.create({**INPUT, "quoteId": quote["id"]}, options={"idempotency_key": "lesson-1"})
            delivered = c.jobs.wait(accepted["id"], options={"poll_interval": .005, "wait_timeout": 1})
            self.assertEqual(delivered["status"], "completed")
            self.assertEqual(c.files.json("file_test"), {"title": "Fractions"})
            destination = Path(directory) / "notes.json"
            c.files.download_to("file_test", destination)
            self.assertEqual(json.loads(destination.read_text()), {"title": "Fractions"})
            with self.assertRaises(FileExistsError): c.files.download_to("file_test", destination)
            self.assertEqual([p.name for p in Path(directory).iterdir()], ["notes.json"])

    def test_read_retry_and_no_mutation_retry(self):
        calls = 0
        def handler(c):
            nonlocal calls
            calls += 1
            return (429, {"error": {"code": "busy"}}, {"retry-after": "0"}) if calls == 1 else ok({"data": []})
        with Fixture(handler) as f, Classive("test", base_url=f.url) as c:
            c.voices.list(); self.assertEqual(calls, 2)
        for status in (429, 500, 503):
            with Fixture(lambda c: (status, {"error": {"code": "busy"}}, {})) as f, Classive("test", base_url=f.url, max_retries=5) as c:
                with self.assertRaises(Exception): c.jobs.create(INPUT, options={"idempotency_key": "same"})
                self.assertEqual(len(f.calls), 1)
        calls = 0
        def disconnect(request):
            nonlocal calls
            calls += 1; raise httpx.ConnectError("disconnected")
        with httpx.Client(transport=httpx.MockTransport(disconnect)) as h, Classive("test", http_client=h, max_retries=1) as c:
            with self.assertRaises(NetworkError): c.jobs.create(INPUT)
            self.assertEqual(calls, 1)
            calls = 0
            with self.assertRaises(NetworkError): c.voices.list()
            self.assertEqual(calls, 2)

    def test_error_types_and_details(self):
        for status, cls in [(401,AuthenticationError),(402,InsufficientCreditsError),(409,ConflictError),(429,RateLimitError),(503,ServiceError)]:
            with Fixture(lambda c: (status,{"error":{"code":"specific","message":"Actionable","details":{"field":"prompt"}}},{"x-request-id":"request_test"})) as f, Classive("test",base_url=f.url,max_retries=0) as c:
                with self.assertRaises(cls) as caught: c.prices.get()
                self.assertEqual(caught.exception.status,status)
                self.assertEqual(caught.exception.code,"specific")
                self.assertEqual(caught.exception.request_id,"request_test")
                self.assertEqual(caught.exception.details["error"]["details"]["field"],"prompt")

    def test_wait_terminal_failures_timeout_and_no_cancellation(self):
        for status, cls in [("failed",JobFailedError),("cancelled",JobCancelledError)]:
            with Fixture(lambda c: ok(job(status))) as f, Classive("test",base_url=f.url) as c:
                with self.assertRaises(cls) as caught: c.jobs.wait("job_test")
                self.assertEqual(caught.exception.job["status"],status)
        with Fixture(lambda c: ok(job("processing"))) as f, Classive("test",base_url=f.url) as c:
            with self.assertRaises(TimeoutError): c.jobs.wait("job_test", options={"wait_timeout":.035,"poll_interval":.005})
            self.assertTrue(all(call["method"] == "GET" for call in f.calls))

    def test_redirect_refusal_preserves_secret_and_cleans_temp_file(self):
        with Fixture(lambda c: ok({})) as target, Fixture(lambda c:(302,b"",{"location":target.url+"/stolen"})) as f, Classive("secret",base_url=f.url) as c, tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ProtocolError): c.files.download("file_test")
            with self.assertRaises(ProtocolError): c.files.download_to("file_test",Path(directory)/"output")
            with self.assertRaises(ValidationError): c.files.download(target.url)
            self.assertEqual(target.calls,[])
            self.assertEqual(list(Path(directory).iterdir()),[])

    def test_upload_wait_and_paginate(self):
        def handle(c):
            if c["method"] == "POST": return ok({"id":"mat_test","status":"queued"})
            if c["url"].path in ("/v1/materials","/v1/jobs"):
                prefix="mat" if "materials" in c["url"].path else "job"
                later="starting_after" in parse_qs(c["url"].query)
                return ok({"data":[{"id":prefix+("_b" if later else "_a")}],"hasMore":not later})
            if c["url"].path.startswith("/v1/curricula"): return ok({"status":"draft"})
            return ok({"status":"ready"})
        with Fixture(handle) as f, Classive("test",base_url=f.url) as c, tempfile.TemporaryDirectory() as directory:
            source=Path(directory)/"source.txt";source.write_text("Fractions ✓")
            c.materials.upload(source,metadata={"rights":"I have permission to use this content."})
            self.assertEqual(base64.b64decode(f.calls[0]["body"]["base64"]).decode(),"Fractions ✓")
            self.assertEqual(c.materials.wait("mat_test")["status"],"ready")
            self.assertEqual([m["id"] for m in c.materials.iterate(query={"search":"math"})],["mat_a","mat_b"])
            self.assertEqual([j["id"] for j in c.jobs.iterate()],["job_a","job_b"])
            self.assertEqual(c.curricula.wait("cur_test")["status"],"draft")

    def test_configuration_and_all_model_annotations(self):
        for key in ("", "cmcp_live_secret"):
            with self.assertRaises(ValidationError): Classive(key)
        for url in ("http://remote.example","https://user:password@example.com","https://example.com/path","https://example.com?token=private"):
            with self.assertRaises(ValidationError): Classive("secret",base_url=url)
        self.assertEqual(types.Audience.__required_keys__, frozenset({"band"}))
        for value in vars(types).values():
            if typing.is_typeddict(value): typing.get_type_hints(value)

    def test_webhook_signatures(self):
        raw='{"event":"é"}';secret="webhook_test";t=1000
        signature=hmac.new(secret.encode(),f"{t}.{raw}".encode(),hashlib.sha256).hexdigest()
        header=f"t={t},v1={signature}"
        self.assertTrue(verify_webhook(raw,header,secret,now=1000))
        self.assertTrue(verify_webhook(raw.encode(),header,secret,now=1000))
        for body,h,now in [(raw+" ",header,1000),(raw,header,2000),(raw,header,0),(raw,"t=1000,v1=no",1000),(raw,header+",v1="+signature,1000)]:
            self.assertFalse(verify_webhook(body,h,secret,now=now))

    def test_documentation_example_quote_only_and_explicit_submission(self):
        spec=importlib.util.spec_from_file_location("lesson_example",ROOT/"examples/python/lesson.py")
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        def handle(call):
            if call["url"].path=="/v1/jobs/quote": return ok({"id":"quo_example","credits":10})
            if call["method"]=="POST": return ok(job("queued"))
            return ok(job())
        with Fixture(handle) as f, Classive("test",base_url=f.url) as c:
            module.run_lesson(c)
            self.assertEqual(len(f.calls),1)
            self.assertEqual(f.calls[0]["url"].path,"/v1/jobs/quote")
            f.calls.clear();module.run_lesson(c,submit=True)
            self.assertEqual(len([call for call in f.calls if call["method"]=="POST" and call["url"].path=="/v1/jobs"]),1)

class AsyncTests(unittest.IsolatedAsyncioTestCase):
    async def test_all_52_operations_over_http(self):
        spec=json.loads((ROOT/"schema/openapi.json").read_text())
        ops=json.loads((ROOT/"schema/operations.json").read_text())
        with Fixture(lambda c:ok({"ok":True})) as f:
            async with AsyncClassive("test",base_url=f.url,max_retries=0) as c:
                for op in ops:
                    schema=spec["paths"][op["path"]][op["method"].lower()]
                    params=schema.get("parameters",[])
                    args=["file_test" if p["name"]=="fileId" else "id_test" for p in params if p["in"]=="path"]
                    body={"marker":op["operationId"]} if "application/json" in schema.get("requestBody",{}).get("content",{}) else None
                    if body is not None: args.append(body)
                    query={p["name"]:True if p["schema"].get("type")=="boolean" else 2 if p["name"]=="limit" else "value" for p in params if p["in"]=="query"}
                    kwargs={"options":{"idempotency_key":"sdk-test"}}
                    if query: kwargs["query"]=query
                    await getattr(getattr(c,op["resource"]),op["python"])(*args,**kwargs)
                    call=f.calls[-1]
                    self.assertEqual(call["method"],op["method"])
                    self.assertEqual(call["url"].path,op["path"].replace("{fileId}","file_test").replace("{id}","id_test"))
                    self.assertEqual(call["body"],body)
                    self.assertEqual(parse_qs(call["url"].query),{k:[str(v).lower() if isinstance(v,bool) else str(v)] for k,v in query.items()})
                    self.assertEqual(call["headers"]["Idempotency-Key"],"sdk-test")

    async def test_async_delivery_and_stream(self):
        reads=0
        def handle(call):
            nonlocal reads
            if call["url"].path=="/v1/jobs/quote": return ok({"id":"quo_test"})
            if call["method"]=="POST": return ok(job("queued"))
            if call["url"].path.startswith("/v1/files"): return ok({"title":"Fractions"})
            reads+=1;return ok(job("processing" if reads==1 else "completed"))
        with Fixture(handle) as f, tempfile.TemporaryDirectory() as directory:
            async with AsyncClassive("test",base_url=f.url) as c:
                quote=await c.jobs.quote(INPUT)
                accepted=await c.jobs.create({**INPUT,"quoteId":quote["id"]},options={"idempotency_key":"lesson-1"})
                delivered=await c.jobs.wait(accepted["id"],options={"poll_interval":.005,"wait_timeout":1})
                self.assertEqual(delivered["status"],"completed")
                output=Path(directory)/"notes.json"
                await c.files.download_to("file_test",output)
                self.assertEqual(json.loads(output.read_text()),{"title":"Fractions"})

    async def test_async_retry_mutation_no_retry_and_cancellation(self):
        calls=0
        async def handle(request):
            nonlocal calls
            calls+=1
            return httpx.Response(429,json={"error":{"code":"busy"}},headers={"retry-after":"0"}) if calls==1 else httpx.Response(200,json={"data":[]})
        async with httpx.AsyncClient(transport=httpx.MockTransport(handle)) as http, AsyncClassive("test",http_client=http) as c:
            await c.voices.list();self.assertEqual(calls,2)
            calls=0
            with self.assertRaises(RateLimitError): await c.jobs.create(INPUT)
            self.assertEqual(calls,1)
        async def slow(request):
            await asyncio.sleep(10);return httpx.Response(200,json=job("processing"))
        async with httpx.AsyncClient(transport=httpx.MockTransport(slow)) as http, AsyncClassive("test",http_client=http,timeout=.02) as c:
            with self.assertRaises(TimeoutError): await c.jobs.get("job_test")
            task=asyncio.create_task(c.jobs.wait("job_test",options={"wait_timeout":2,"timeout":1}))
            await asyncio.sleep(.005);task.cancel()
            with self.assertRaises(asyncio.CancelledError): await task

    async def test_async_redirect_and_partial_file_cleanup(self):
        class BrokenStream(httpx.AsyncByteStream):
            async def __aiter__(self):
                yield b"partial"
                raise httpx.ReadError("stream ended")
        async def handle(request): return httpx.Response(200,stream=BrokenStream())
        with tempfile.TemporaryDirectory() as directory:
            async with httpx.AsyncClient(transport=httpx.MockTransport(handle)) as http, AsyncClassive("test",http_client=http,max_retries=0) as c:
                with self.assertRaises(NetworkError): await c.files.download_to("file_test",Path(directory)/"out")
                self.assertEqual(list(Path(directory).iterdir()),[])

if __name__ == "__main__": unittest.main()

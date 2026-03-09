# hello-worker (Go)

Minimal WCP-compliant worker written in Go using the [pyhall-go SDK](https://github.com/pyhall/pyhall-go).

## Requirements

```bash
go get github.com/pyhall/pyhall-go
```

## Run

```bash
WCP_ATTEST_HMAC_KEY=devsecret go run worker.go
```

## Test

```bash
curl -X POST http://localhost:8080/run \
  -H "Content-Type: application/json" \
  -d '{"input": "hello"}'
```

## Enroll in Hall

```bash
pyhall enroll --id org.example.hello-worker.instance-1 \
              --species wrk.doc.summarizer \
              --endpoint http://localhost:8080/run
```

## Docs

[pyhall.dev/docs](https://pyhall.dev/docs/getting-started/)

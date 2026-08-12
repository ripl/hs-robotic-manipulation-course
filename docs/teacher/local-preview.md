# Local Preview

Use these commands when editing or reviewing the documentation site locally.

## Start the Site

From the repository root:

```bash
cd hs-robotic-manipulation-course
source .docs-venv/bin/activate
mkdocs serve
```

Then open:

```text
http://127.0.0.1:8000/
```

The terminal running `mkdocs serve` is the server process. Leave that terminal open while previewing.

## Stop the Site

If `mkdocs serve` is running in the foreground, press:

```text
Control-C
```

## Find the Running Process

To see the MkDocs process and PID:

```bash
ps -axo pid,ppid,stat,command | grep '[m]kdocs serve'
```

To see which process is listening on port 8000:

```bash
lsof -iTCP:8000 -sTCP:LISTEN -n -P
```

## Stop by PID

If the site is running in another terminal or the port is stuck, find the PID and stop it:

```bash
kill PID
```

Replace `PID` with the number from `ps` or `lsof`.

If it does not stop after a few seconds:

```bash
kill -9 PID
```

Prefer `Control-C` or `kill PID` first. Use `kill -9` only for a stuck process.

## Build Without Serving

To check the site without launching a local server:

```bash
source .docs-venv/bin/activate
mkdocs build --strict
```

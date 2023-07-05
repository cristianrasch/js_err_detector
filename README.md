# JS error detector

## Installation

1. Create a new Python virtual environment:

```bash
python3 -m venv .venv
```

2. Activate the Python virtual environment:

```bash
. .venv/bin/activate
```

3. Install the Python dependencies:

```bash
python3 -m pip install -r requirements.txt
```

4. Let playwright install the browser(s) you want to use:

```bash
python3 -m playwright install firefox chromium
```

5. Read the usage instructions:

```bash
./app.py -h
```

Example usage:

```bash
./app.py -b chromium -u https://www.1point21interactive.com/
```

## Notes

* Errors are logged to STDERR.
* The script finishes with a non-zero status code if at least 1 JS error was detected.

check-gce-cpu.py

# Install
`pip install -r requirements.txt`

## Dependency

- > Python 2.7
- pytz
- google-api-python-client

# Run
`./check-gce-cpu.py -p <hogehoge> -H <fugafuga>`

## Args
See `./check-gce-cpu.py -h` .

### `-p` project_id
Suport both `numeric only` and `strings (with hyphenated)`.
Run at GCE-VM, get it from meta-data automaticaly.

### `-H` hostname
Run at GCE-VM, get from meta-data automaticaly.

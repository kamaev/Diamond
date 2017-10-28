<!--This file was generated from the python source
Please edit the source to make changes
-->
DirStatsCollector
=====

Collect given directories stats.


#### Options

Setting | Default | Description | Type
--------|---------|-------------|-----
byte_unit | byte | Default numeric output(s) | str
dirs | {} | directories to collect stats on | dict
enabled | False | Enable collecting these metrics | bool
measure_collector_time | False | Collect the collector run time in ms | bool
metrics_blacklist | None | Regex to match metrics to block. Mutually exclusive with metrics_whitelist | NoneType
metrics_whitelist | None | Regex to match metrics to transmit. Mutually exclusive with metrics_blacklist | NoneType

#### Example Output

```
servers.hostname.logs.current_size 18
servers.hostname.logs.days_unmodified 1
servers.hostname.subdirs 5
servers.hostname.files 18
```

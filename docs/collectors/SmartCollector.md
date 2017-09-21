<!--This file was generated from the python source
Please edit the source to make changes
-->
SmartCollector
=====

Collect data from S.M.A.R.T.'s attribute reporting.

#### Dependencies

 * [smartmontools](http://sourceforge.net/apps/trac/smartmontools/wiki)


#### Options

Setting | Default | Description | Type
--------|---------|-------------|-----
aliases | {} | Aliases to assign | dict
attributes | {} | Attributes to publish | dict
bin | smartctl | The path to the smartctl binary | str
byte_unit | byte | Default numeric output(s) | str
devices | ['sda'] | Devices to collect stats on | list
force_prefails | False | Fetch prefails anyway | bool
enabled | False | Enable collecting these metrics | bool
measure_collector_time | False | Collect the collector run time in ms | bool
sudo_cmd | /usr/bin/sudo | Path to sudo | str
metrics_blacklist | None | Regex to match metrics to block. Mutually exclusive with metrics_whitelist | NoneType
metrics_whitelist | None | Regex to match metrics to transmit. Mutually exclusive with metrics_blacklist | NoneType
use_sudo | False | Use sudo? | bool
valtypes | value, worst, thresh, raw_val | Values to publish | list

#### Example Output

```
path_prefix.hostname.sda.pre-fail.value.raw_read_error_rate 100
path_prefix.hostname.sda.pre-fail.worst.raw_read_error_rate 100
path_prefix.hostname.sda.pre-fail.thresh.raw_read_error_rate 16
path_prefix.hostname.sda.pre-fail.raw_val.raw_read_error_rate  0
path_prefix.hostname.sda.pre-fail.value.throughput_performance 138
path_prefix.hostname.sda.pre-fail.worst.throughput_performance 138
path_prefix.hostname.sda.pre-fail.thresh.throughput_performance 54
path_prefix.hostname.sda.pre-fail.raw_val.throughput_performance 100
path_prefix.hostname.sda.old-age.value.start_stop_count 100
path_prefix.hostname.sda.old-age.worst.start_stop_count 100
path_prefix.hostname.sda.old-age.thresh.start_stop_count 0
path_prefix.hostname.sda.old-age.raw_val.start_stop_count 11
path_prefix.hostname.sda.pre-fail.value.some_attribute 153
path_prefix.hostname.sda.pre-fail.worst.some_attribute 153
path_prefix.hostname.sda.pre-fail.thresh.some_attribute 24
path_prefix.hostname.sda.pre-fail.raw_val.some_attribute 396
```

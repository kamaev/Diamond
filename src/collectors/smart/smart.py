# coding=utf-8

"""
Collect data from S.M.A.R.T.'s attribute reporting.

#### Dependencies

 * [smartmontools](http://sourceforge.net/apps/trac/smartmontools/wiki)

"""

import subprocess
import os
import diamond.collector


class SMARTAttribute(object):
    """
    S.M.A.R.T. attribute object.
    """
    def __init__(self,
                 instance):

        self.instance = instance
        self.name = self.instance[1].lower()
        self.value = int(self.instance[3])
        self.worst = int(self.instance[4])
        self.thresh = int(self.instance[5])
        self.priority = self.instance[6].lower()

        if self.name == 'unknown_attribute':
            self.attribute = self.instance[0]
        else:
            self.attribute = self.name

        if '/' not in self.instance[9]:
            self.raw_val = int(self.instance[9])
        else:
            try:
                num, denom = self.instance[9].split('/')
                self.raw_val = 100*(int(num)/int(denom))
            except ZeroDivisionError:
                self.raw_val = 0


class SmartCollector(diamond.collector.Collector):
    """
    Collector subclass of diamond.collector.Collector.
    """
    def __init__(self, *args, **kwargs):
        super(SmartCollector, self).__init__(*args, **kwargs)
        self.metrics = {}

    def get_default_config_help(self):
        """
        Returns the help text for the configuration options for this collector.
        """
        config_help = super(SmartCollector, self).get_default_config_help()
        config_help.update({
            'devices': "Devices to collect stats on",
            'bin': 'The path to the smartctl binary',
            'use_sudo': 'Use sudo?',
            'sudo_cmd': 'Path to sudo',
            'attributes': 'Attributes to publish',
            'aliases': 'Aliases to assign',
            'valtypes': 'Values to publish',
            'force_prefails': 'Fetch prefails anyway'})

        return config_help

    def get_default_config(self):
        """
        Returns default configuration options.
        """
        config = super(SmartCollector, self).get_default_config()
        config.update({
            'devices': ['sda'],
            'bin': 'smartctl',
            'use_sudo': False,
            'sudo_cmd': '/usr/bin/sudo',
            'attributes': {},
            'aliases': {},
            'valtypes': ['value', 'worst', 'thresh', 'raw_val'],
            'force_prefails': False})

        return config

    def find_attr_start_line(self, lines, min_line=4, max_line=9):
        """
        Return line number of the first real attribute and value.
        The first line is 0.  If the 'ATTRIBUTE_NAME' header is not
        found, return the index after max_line.
        """
        for idx, line in enumerate(lines[min_line:max_line]):
            col = line.split()
            if len(col) > 1 and col[1] == 'ATTRIBUTE_NAME':
                return idx + min_line + 1

        self.log.warn('ATTRIBUTE_NAME not found in second column of'
                      ' smartctl output between lines %d and %d.'
                      % (min_line, max_line))

        return max_line + 1

    def convert_to_metric(self, device, smart):
        """
        Converts fetched data into graphite metric format.
        """
        if device in self.config['aliases'] and \
           smart.attribute in self.config['aliases'][device]:
            smart.attribute = self.config['aliases'][device][smart.attribute]

        for valtype in self.config['valtypes']:
            metric = "%s.%s.%s.%s" % (device, smart.priority, valtype,
                                      smart.attribute)

            self.metrics[metric] = getattr(smart, valtype)

    def fetch_data(self, device):
        """
        Fetching S.M.A.R.T. data.
        """
        if self.config['force_prefails']:
            critical = 'pre-fail'
        else:
            critical = None

        command = [self.config['bin'], "-A", os.path.join('/dev', device)]

        if diamond.collector.str_to_bool(self.config['use_sudo']):
            command.insert(0, self.config['sudo_cmd'])

        attributes = subprocess.Popen(
            command,
            stdout=subprocess.PIPE
            ).communicate()[0].strip().splitlines()

        start_line = self.find_attr_start_line(attributes)

        for attr in attributes[start_line:]:
            smart = SMARTAttribute(instance=attr.split())
            if smart.priority == critical or \
               smart.attribute in self.config['attributes'] and \
               self.config['attributes'][smart.attribute]:
                self.convert_to_metric(device, smart)

    def collect(self):
        """
        Collect and publish S.M.A.R.T. attributes.
        """
        for device in self.config['devices']:
            self.fetch_data(device)

        for metric in self.metrics:
            self.publish(metric, self.metrics[metric])

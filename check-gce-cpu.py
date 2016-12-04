#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import httplib2
from apiclient import discovery
from oauth2client.client import GoogleCredentials
import pytz
import datetime
import sys


def get_meta(path):
    http = httplib2.Http()
    url = "http://metadata.google.internal/computeMetadata/v1/{0}".format(path)
    resp, content = http.request(
        url, "GET", headers={'Metadata-Flavor': 'Google'})
    if resp["status"] != "200":
        raise Exception("Unable to get metadata %s" % url)
    return content


def main():
    try:
        # arguments
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "-w", "--warning",
            help="warning (percent default:80)",
            type=int,
            default=80
            )
        parser.add_argument(
            "-c", "--critical",
            help="critical (percent default:90)",
            type=int,
            default=90
            )
        parser.add_argument(
            "-p", "--projectid",
            help="GCE project ID"
            )
        parser.add_argument(
            "-H", "--hostname",
            help="GCE hostname (metric.label.instance_name)"
            )
        args = parser.parse_args()
        warn = args.warning
        crit = args.critical
        project_id = args.projectid
        if not project_id:
            project_id = get_meta('project/numeric-project-id')
        hostname = args.hostname
        if not hostname:
            hostname = get_meta('instance/hostname').split('.')[0]

        credentials = GoogleCredentials.get_application_default()
        service = discovery.build('monitoring', 'v3', credentials=credentials)

        project_resource = "projects/{0}".format(project_id)
        end_time = datetime.datetime.now(pytz.utc) - datetime.timedelta(minutes=1)
        end_time = end_time.replace(second=0, microsecond=0)
        start_time = end_time - datetime.timedelta(minutes=2)
        fl_s = ('metric.type="compute.googleapis.com/instance/cpu/utilization"'
                ' AND metric.label.instance_name="{0}"').format(hostname)

        req = service.projects().timeSeries().list(
            name=project_resource,
            filter=fl_s,
            interval_endTime=end_time.isoformat(),
            interval_startTime=start_time.isoformat(),
            fields="timeSeries.points.value"
            )
        ret = req.execute()
        raw_val = ret[u'timeSeries'][0][u'points'][0][u'value'][u'doubleValue']
        val = raw_val * 100

        if val > crit:
            print "CheckCPU CRITICAL - {0}".format(val)
            sys.exit(2)
        if val > warn:
            print "CheckCPU WARNING - {0}".format(val)
            sys.exit(1)
        print "CheckCPU OK - {0}".format(val)

    except Exception as e:
        print "fail to get monitoring-value: exception=%s" % e

if __name__ == "__main__":
    main()

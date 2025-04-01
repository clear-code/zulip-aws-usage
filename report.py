#!/usr/bin/env python3

import sys
import os
import argparse
import datetime
import boto3
import zulip
import yaml


BASEDIR = os.path.dirname(sys.argv[0])
CONFIG_FILE = os.path.join(BASEDIR, 'config.yaml')


class AWSUsage(object):
    def __init__(self, account_id, use_default_session=False):
        self._account_id = account_id
        self._use_default_session = use_default_session
        self._custom_session = None
        self._profile_name = 'default'

    def set_profile_name(self, name):
        if self._use_default_session:
            raise RuntimeError("Cannot set profile name when using default session.")
        self._profile_name = name

    def get_monthly_cost(self):
        client= self._get_client('budgets')
        resp = client.describe_budgets(AccountId=self._account_id)
        cost = resp['Budgets'][0]['CalculatedSpend']['ActualSpend']['Amount']
        forecast = resp['Budgets'][0]['CalculatedSpend']['ForecastedSpend']['Amount']
        return (float(cost), float(forecast))

    def get_server_stats(self):
        client= self._get_client('ec2')
        resp = client.describe_instances()
        nserver = 0
        for resv in resp['Reservations']:
            for inst in resv['Instances']:
                if inst['State']['Name'] != 'terminated':
                    nserver += 1
        return nserver

    def _get_client(self, name):
        if self._use_default_session:
            return boto3.client(name)
        custom_session = self._get_custom_session()
        return custom_session.client(name)

    def _get_custom_session(self):
        if self._custom_session is None:
            self._custom_session = boto3.Session(profile_name=self._profile_name)
        return self._custom_session


def load_config():
    with open(CONFIG_FILE) as fp:
        return yaml.load(fp, Loader=yaml.Loader)

def send_message(config, message):
    client = zulip.Client(site=config['zulip']['site'],
                          email=config['zulip']['email'],
                          api_key=config['zulip']['api_key'],
                          insecure=False)
    client.send_message({
        'type': config['zulip']['type'],
        'to': [config['zulip']['to']],
        'topic': config['zulip']['topic'],
        'content': message
    })

def format_message(config, cost, forecast, nserver):
    today = datetime.date.today()
    template = config['zulip']['message']
    return template.format(year=today.year, month=today.month, day=today.day,
                           cost=cost, forecast=forecast, nserver=nserver)

def main(aws_profile_name='default', use_aws_default_session=False, dryrun=False):
    config = load_config()

    aws_usage = AWSUsage(config['aws']['account_id'], use_aws_default_session)
    if not use_aws_default_session:
        aws_usage.set_profile_name(aws_profile_name)
    cost, forecast = aws_usage.get_monthly_cost()
    nserver = aws_usage.get_server_stats()

    message = format_message(config, cost, forecast, nserver)
    if dryrun:
        print(message)
    else:
        send_message(config, message)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--aws-profile', type=str, default='default',
        help="AWS profile name. Default: 'default'.")
    parser.add_argument('--use-aws-default-session', action='store_true',
        help="Use default session to connect AWS. --aws-profile is ignored.")
    parser.add_argument('--dryrun', action='store_true',
        help="For debug. Print the message to stdout.")
    args = parser.parse_args()

    main(args.aws_profile, args.use_aws_default_session, args.dryrun)

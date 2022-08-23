#!/usr/bin/env python3

import sys
import os
import datetime
import boto3
import zulip
import yaml

BASEDIR = os.path.dirname(sys.argv[0])
CONFIG_FILE = os.path.join(BASEDIR, 'config.yaml')

def load_config():
    with open(CONFIG_FILE) as fp:
        return yaml.load(fp, Loader=yaml.Loader)

def get_monthly_cost(config):
    client = boto3.client("budgets")
    resp = client.describe_budgets(AccountId=config['aws']['account_id'])
    cost = resp['Budgets'][0]['CalculatedSpend']['ActualSpend']['Amount']
    forecast = resp['Budgets'][0]['CalculatedSpend']['ForecastedSpend']['Amount']
    return (float(cost), float(forecast))

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

def format_message(config, cost, forecast):
    today = datetime.date.today()
    template = config['zulip']['message']
    return template.format(year=today.year, month=today.month, day=today.day,
                           cost=cost, forecast=forecast)

def main():
    config = load_config()
    cost, forecast = get_monthly_cost(config)
    message = format_message(config, cost, forecast)
    send_message(config, message)

if __name__ == '__main__':
    main()

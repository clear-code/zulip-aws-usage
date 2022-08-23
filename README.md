# zulip-aws-usage

Programatically send AWS usage report to Zulip.

## QuickStart

1. Set up an AWS access key.

   ```console
   $ cat ~/.aws/credentials
   [default]
   aws_access_key_id = xxx
   aws_secret_access_key = xxx
   region = ap-northeast-1
   ```

2. Create a bot on Zulip.

   * Visit "Settings > Personal > Bot" and create a "Generic" bot.

3. Set up your notification configuration.

   ```console
   $ cp config.yaml.tmpl
   $ vim config.yaml
   ```

4. Run pip install and run report.py.

   ```console
   $ python3 -u pip install -r requirments.txt
   $ python3 report.py
   ```

## HowTo Guides

### How to fix "Permission denied" error on AWS

You need `AWSBudgetsReadOnlyAccess` to fetch the AWS usage data.

Check your current permission policy on IAM > Users.

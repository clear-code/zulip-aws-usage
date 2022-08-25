# zulip-aws-usage

Programatically send AWS usage report to Zulip.

## QuickStart

1. Set up an AWS access key.

   * If you don't have `AWS CLI`, then install it.
      * https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html

   ```console
   $ aws configure
   $ cat ~/.aws/credentials
   [default]
   aws_access_key_id = xxx
   aws_secret_access_key = xxx
   $ cat ~/.aws/config
   [default]
   region = ap-northeast-1
   ```

2. Prepare a bot on Zulip.

   * Visit "Settings > Personal > Bot" and create an "incoming webhook" bot.

3. Set up your notification configuration.

   ```console
   $ cp config.yaml.tmpl config.yaml
   $ vim config.yaml
   ```

4. Run pip install and run report.py.

   ```console
   $ python3 -m pip install -r requirments.txt
   $ python3 report.py
   ```

## HowTo Guides

### How to send a test message

You can send reports to yoru private chat by setting `zulip.type` to `private`.
See [Zulip API documentation](https://zulip.com/api/send-message) for details.

```yaml
zulip:
  ...
  type: "private"
  to: "my-name@example.com"
  topic: ""
  ...
```

### How to fix "Permission denied" error on AWS

You need `AWSBudgetsReadOnlyAccess` to fetch the AWS usage data.

Check your current permission policy on IAM > Users.

### How to schedule bot execution

Install the service definition files:

```console
$ mkdir -p ~/.config/systemd/user/
$ cp systemd/zulip-aws-usage.* ~/.config/systemd/user/
```

Fix the script path in `ExecStart`:

```console
$ vim ~/.config/systemd/user/zulip-aws-usage.service
```

Check if the service works:

```console
$ systemctl start --user zulip-aws-usage.service
```

If it worked, enable the timer:

```console
$ systemctl enable --user zulip-aws-usage.timer
$ systemctl start --user zulip-aws-usage.timer
```

You can check the execution schedule as follows:

```console
$ systemctl list-timers --user
```

## License

```
Copyright (C) 2022 Daijiro Fukuda <fukuda@clear-code.com>
Copyright (C) 2022 Fujimoto Seiji <fujimoto@clear-code.com>

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License v2.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
```

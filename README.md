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

   * If need, you can use multiple profiles.

   ```console
   $ aws configure --profile bot
   $ cat ~/.aws/credentials
   [default]
   aws_access_key_id = xxx
   aws_secret_access_key = xxx
   [bot]
   aws_access_key_id = xxx
   aws_secret_access_key = xxx
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

   * If you need to use multiple AWS profiles, you can use `--aws-profile` option to specify the profile.

   ```console
   $ python3 report.py --aws-profile bot
   ```

## Environmental variables

You can overwrite each config by the following environmental variables.

|   Env var name   |   Config name    |
|------------------|------------------|
| `AWS_ACCOUNT_ID` | `aws.account_id` |
| `ZULIP_SITE`     | `zulip.site`     |
| `ZULIP_EMAIL`    | `zulip.email`    |
| `ZULIP_API_KEY`  | `zulip.api_key`  |
| `ZULIP_TYPE`     | `zulip.type`     |
| `ZULIP_TO`       | `zulip.to`       |
| `ZULIP_TOPIC`    | `zulip.topic`    |
| `ZULIP_MESSAGE`  | `zulip.message`  |

Please see `config.yaml.tmpl` for an example value.

You can run this script without the config file.
It would be suitable for CI execution.

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

You need `AWSBudgetsReadOnlyAccess` and ` AmazonEC2ReadOnlyAccess` to fetch the AWS usage data.

Check your current permission policy on IAM > Users.

### How to schedule bot execution

* systemd
* GitHub Actions

#### systemd

Install the service definition files:

```console
$ mkdir -p ~/.config/systemd/user/
$ cp systemd/zulip-aws-usage.* ~/.config/systemd/user/
```

Fix the script path or options for the script in `ExecStart`:

```console
$ vim ~/.config/systemd/user/zulip-aws-usage.service
```

Check if the service works:

```console
$ systemctl start --user zulip-aws-usage.service
```

If it worked, enable the timer:

```console
$ systemctl enable --now --user zulip-aws-usage.timer
```

You can check the execution schedule as follows:

```console
$ systemctl list-timers --user
```

#### GitHub Actions (Use OpenID Connect)

This section explains the way to use OpenID Connect without using access keys.
Please handle AWS authentication at your own risk, making sure you understand the official documentation beforehand.

1. Set up AWS Identity providers and Roles with reference to the following documents.
   * [Configuring OpenID Connect in Amazon Web Services](https://docs.github.com/en/actions/security-for-github-actions/security-hardening-your-deployments/configuring-openid-connect-in-amazon-web-services)
1. Create an empty GitHub repository.
1. Set each config of this script to GitHub Actions secrets and variables.
   * Repository variables
     * `ZULIP_MESSAGE`
     * `ZULIP_TO`
     * `ZULIP_TOPIC`
     * `ZULIP_TYPE`
   * Secrets variables
     * `AWS_ACCOUNT_ID`
     * `ZULIP_API_KEY`
     * `ZULIP_EMAIL`
     * `ZULIP_SITE`
1. Set the role name you set up to secrets so that you can use it on the CI setting.
   * For example, the name like `AWS_ASSUME_ROLE_NAME`.
1. Set up GitHub actions to run this script.
   * Checkout this repository.
   * Configure AWS Credentials with reference to [Configuring OpenID Connect in Amazon Web Services](https://docs.github.com/en/actions/security-for-github-actions/security-hardening-your-deployments/configuring-openid-connect-in-amazon-web-services).
     * Use [aws-actions/configure-aws-credentials](https://github.com/aws-actions/configure-aws-credentials).
   * Run this script with `--use-aws-default-session` option.

Example:

```yaml
name: Report
on:
  schedule:
    - cron: '0 9 * * *'
  workflow_dispatch:
permissions:
  id-token: write
  contents: read
jobs:
  report:
    name: Report
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          repository: clear-code/zulip-aws-usage
      - name: Configure AWS Credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-region: (AWS-REGION)
          role-to-assume: arn:aws:iam::${{ secrets.AWS_ACCOUNT_ID }}:role/${{ secrets.AWS_ASSUME_ROLE_NAME }}
      - name: Install requirments
        run: |
          pip install -r requirements.txt
      - name: Report usage
        run: |
          python report.py --use-aws-default-session
        env:
          AWS_ACCOUNT_ID: ${{ secrets.AWS_ACCOUNT_ID }}
          ZULIP_SITE: ${{ secrets.ZULIP_SITE }}
          ZULIP_EMAIL: ${{ secrets.ZULIP_EMAIL }}
          ZULIP_API_KEY: ${{ secrets.ZULIP_API_KEY }}
          ZULIP_TYPE: ${{ vars.ZULIP_TYPE }}
          ZULIP_TO: ${{ vars.ZULIP_TO }}
          ZULIP_TOPIC: ${{ vars.ZULIP_TOPIC }}
          ZULIP_MESSAGE: ${{ vars.ZULIP_MESSAGE }}
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

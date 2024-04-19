# Macのバッテリー容量を元に電源をON/OFFします

poetryを使用します
```bash
pip install poetry
# curl -sSL https://install.python-poetry.org | python3 -

poetry install --no-root

cp .envrc{.sample,}
```

## local起動
```bash
cd /mac_battery_percentage
python src/main.py
```

## cron
```bash
# /usr/sbin/cronをフルディスクアクセス許可しておく
$ crontab -e

# python コマンドへのfull pathか、環境変数をreloadして付与するかをして、パスを通して起動する.
# python, direnvコマンドが必要
*/5 8-23 * * * cd ~/ghq/github.com/orug8m/mac_battery_percentage && /usr/local/bin/direnv exec . ~/.anyenv/envs/pyenv/shims/python src/main.py
```

## linter
```
flake8 . && black . && isort .
```

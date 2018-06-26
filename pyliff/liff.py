#!/bin/env python

import sys
import json
from os import path
from string import Template
import requests

LIFF_BASE_URL = "https://api.line.me/liff/v1/apps"

KEY_LIFF_ID = "liffId"
KEY_VIEW = "view"
KEY_TYPE = "type"
KEY_URL = "url"
KEY_APPS = "apps"
KEY_MESSAGE = "message"

class LiffClient:

    home = path.expanduser("~")
    setting_file = path.join(home, ".liff")
    tokens = {}
    default = ""

    def __init__(self):
        try:
            self._load_settings()
            self.default_token = self.tokens[self.default]
        except Exception as error:
            """"""

    def _load_settings(self):
        with open(self.setting_file, "r") as json_file:
            settings = json.load(json_file)
            self.tokens = settings["tokens"]
            self.default = settings["default"]

    def add_access_token(self, name, token):
        if name in self.tokens:
            print("[WARNING] the name is existed, overwrite the token")

        self.tokens[name] = token
        self.default = name
        self._serialize()

    def delete_access_token(self, name):
        key_to_delete = ""
#       cannot change the size of dict during iteration
        for key in self.tokens:
            if name == key:
                print("delete the token of " + name)
                key_to_delete = key

        if key_to_delete:
            del self.tokens[key_to_delete]
            if self.default == name:
                all_keys = list(self.tokens.keys())
                if len(all_keys) > 0:
                    self.default = all_keys[-1]
                    self.default_token = self.tokens[self.default]

            self._serialize()
        else:
            print("No token found for " + name)

    def _serialize(self):
        json_data = {"default": self.default, "tokens": self.tokens}
        with open(self.setting_file, "w") as json_file:
            json.dump(json_data, json_file, indent=4)

    def set_default_token(self, name):
        if name in self.tokens:
            self.default = name
            self._serialize()
        else:
            print("No token for " + name)

    def list_all_tokens(self):
        if len(self.tokens) == 0:
            print("No tokens")
            return

        for key in self.tokens:
            output = "[{0}]: {1}".format(key, self.tokens[key])
            if key == self.default:
                output = "* " + output
            else:
                output = "  " + output

            print(output)

    def create_liff_app(self, url, size):
        if not self._verify_size(size):
            print("The value of size is incorrect, it must be 'full', 'tall' or 'compact'")
            return

        payload = {KEY_VIEW: {KEY_TYPE: size, KEY_URL: url}}
        response = requests.post(LIFF_BASE_URL, headers=self._default_headers(), json=payload)
        json_response = json.loads(response.text)
        if response.status_code != 200:
            print("Could not create LIFF app. Reason: " + json_response[KEY_MESSAGE])
            sys.exit(1)
        else:
            print("Create LIFF app successfully, id: " + json_response[KEY_LIFF_ID])

    def delete(self, liffId):
        """"""

    def update(self, liffId):
        """"""
    def list(self):
        response_template = Template(APP_INFO_TEMPLATE)
        response = requests.get(LIFF_BASE_URL, headers=self._default_headers())
        json_response = json.loads(response.text)
        apps = json_response[KEY_APPS]
        for app in apps:
            print(response_template.substitute(
                liff_id=app[KEY_LIFF_ID], view_type=app[KEY_VIEW][KEY_TYPE], url=app[KEY_VIEW][KEY_URL]))

    def _verify_size(self, size):
        return size == "full" or size == "compact" or size == "tall"

    def _default_headers(self):
        return {"Authorization": "Bearer " + self.default_token,
                "Content-Type": "application/json"}


APP_INFO_TEMPLATE = """
  id: $liff_id,
  viewType: $view_type,
  url: $url"""

TOKEN_USAGE = """  liff token add <name> <token>       Add new access token, the new token will be the default token
  liff token delete <name>            Delete the access token. If it is default token, the last added token would become default token
  liff token set-default <name>       Set the default token       
  liff token list                     List all tokens
"""

LIFF_APP_USAGE = """  liff create[c] <url> <type>[compact, tall, full]
  liff list[l]
  liff delete[d] <liff_id>
  liff update[u] <liff_id> json_of_items_to_change
"""

ALL_USAGE = Template("""usage: liff <command> [<args>]

Token managements:
$token_usage
LIFF app managements
$liff_app_usage
""").substitute(token_usage=TOKEN_USAGE, liff_app_usage=LIFF_APP_USAGE)


def run_token_command(client, subcommand, args):
    if subcommand == "add" or subcommand == "a" and len(args) == 2:
        client.add_access_token(args[0], args[1])
    elif subcommand == "delete" or subcommand == "d" and len(args) == 1:
        client.delete_access_token(args[0])
    elif subcommand == "set-default" and len(args) == 1:
        client.set_default_token(args[0])
    elif subcommand == "list" and len(args) == 0:
        client.list_all_tokens()
    else:
        print("usage:\n" + TOKEN_USAGE)


def run_command(command, args):
    client = LiffClient()
    if command == "token" or command == "t":
        if len(args) < 1:
            print("usage:\n" + TOKEN_USAGE)
            return

        run_token_command(client, args[0], args[1:])
    elif command == "list" or command == "l":
        liffs = client.list()
    elif command == "create" or command == "c":
        if len(args) < 2:
            print("usage:\n" + LIFF_APP_USAGE)
            return

        client.create_liff_app(url=args[0], size=args[1])
    elif command == "delete" or command == "d":
        client.delete(sys.argv[2])
    elif command == 'update' or command == "u" and len(args) == 3:
        client.update(sys.argv[2])
    else:
        print(ALL_USAGE)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(ALL_USAGE)
        sys.exit(1)

    run_command(sys.argv[1], sys.argv[2:])

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

APP_INFO_TEMPLATE = """
  id: $liff_id,
  viewType: $view_type,
  url: $url"""


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
            self.default_token = ""

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

    def create_app(self, url, size):
        if not self._verify_view_size(size):
            print("The value of size is incorrect, it must be 'full', 'tall' or 'compact'")
            return

        def success_handler(json):
            print("Create LIFF app successfully, id: " + json[KEY_LIFF_ID])

        def error_handler(json):
            print("Could not create LIFF app. Reason: " + json[KEY_MESSAGE])
            sys.exit(1)

        payload = {KEY_VIEW: {KEY_TYPE: size, KEY_URL: url}}
        response = requests.post(LIFF_BASE_URL, headers=self._default_headers(), json=payload)
        self._handle_response(response, success_handler, error_handler)

    def delete_app(self, liff_id):

        def success_handler(json):
            print("Delete LIFF app successfully")

        def error_handler(json):
            print("Could not delete LIFF app. Reason: " + json[KEY_MESSAGE])
            sys.exit(1)

        response = requests.delete(LIFF_BASE_URL + "/{0}".format(liff_id), headers=self._default_headers())
        self._handle_response(response, success_handler, error_handler)

    def update_app(self, liff_id, properties):
        if not properties:
            print("The new value is empty, skip")
            return

        def success_handler(json):
            print("Update successfully")

        def error_handler(json):
            print("Cannot update LIFF app. Reason: " + json[KEY_MESSAGE])
            sys.exit(1)

        payload = self._generate_json_for_update(properties)
        response = requests.put(
            LIFF_BASE_URL + "/{0}/view".format(liff_id),
            headers=self._default_headers(),
            json=payload
        )
        self._handle_response(response, success_handler, error_handler)

    def _generate_json_for_update(self, properties):
        new_properties = properties.split(",")
        new_values = {}
        for property in new_properties:
            key_value = property.strip().split(":", maxsplit=1)
            if len(key_value) != 2:
                print("Incorrect value format for updating liff application")
                sys.exit(1)
            key = key_value[0].strip()
            value = key_value[1].strip()
            if self._verify_key_and_value(key, value):
                new_values[key] = value

        return new_values

    def _verify_key_and_value(self, key, value):
        if not key == KEY_TYPE and not key == KEY_URL:
            return False
        if key == KEY_TYPE and not self._verify_view_size(value):
            print("The value of size is incorrect, it must be 'full', 'tall' or 'compact'")
            sys.exit(1)

        return True

    def list_all_apps(self):
        if not self.default_token:
            print("Please set access token first, run liff token add <name> <token>")
            sys.exit(1)

        response_template = Template(APP_INFO_TEMPLATE)
        response = requests.get(LIFF_BASE_URL, headers=self._default_headers())

        def success_handler(json):
            if KEY_APPS not in json:
                print("No LIFF application now, use 'liff create' to create a new LIFF application.")

            apps = json[KEY_APPS]
            for app in apps:
                print(response_template.substitute(
                    liff_id=app[KEY_LIFF_ID], view_type=app[KEY_VIEW][KEY_TYPE], url=app[KEY_VIEW][KEY_URL]))

        def error_handler(json):
            print("Could not list LIFF app. Reason: " + json[KEY_MESSAGE])
            sys.exit(1)

        self._handle_response(response, success_handler, error_handler)

    def _verify_view_size(self, size):
        return size == "full" or size == "compact" or size == "tall"

    def _default_headers(self):
        return {"Authorization": "Bearer " + self.default_token,
                "Content-Type": "application/json"}

    def _handle_response(self, response, success_handler, error_handler):
        try:
            json_response = json.loads(response.text)
        except json.JSONDecodeError:
            json_response = ""
        if response.status_code != 200:
            error_handler(json_response)
        else:
            success_handler(json_response)

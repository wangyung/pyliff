#!/bin/env python

import sys
from string import Template
from liffclient import LiffClient


TOKEN_USAGE = """  liff token add <name> <token>                     Add new access token, the new token will be the default token
  liff token[t] delete <name>                       Delete the access token. If it is default token, the last added token would become default token
  liff token[t] set-default <name>                  Set the default token       
  liff token[t] list                                List all tokens
"""

LIFF_APP_USAGE = """  liff create[c] <url> <type>[compact, tall, full]     Create a new LIFF application.
  liff list[l]                                         List all LIFF applications
  liff delete[d] <id>                                  Delete a LIFF application.
  liff update[u] <id> <new_values>                     Update the LIFF application with new values. The value format is PROPERTY:VALUE and use the comma to seperate each value
  Example: 
      liff update 1234567 url:https://test.com,type:full
"""

ALL_USAGE = Template("""usage: liff <command> [<args>]

Token managements:
$token_usage
LIFF app managements
$liff_app_usage
""").substitute(token_usage=TOKEN_USAGE, liff_app_usage=LIFF_APP_USAGE)


def run_token_command(client, subcommand, args):
    if (subcommand == "add" or subcommand == "a") and len(args) == 2:
        client.add_access_token(args[0], args[1])
    elif (subcommand == "delete" or subcommand == "d") and len(args) == 1:
        client.delete_access_token(args[0])
    elif subcommand == "set-default" and len(args) == 1:
        client.set_default_token(args[0])
    elif (subcommand == "list" or subcommand == "l") and len(args) == 0:
        client.list_all_tokens()
    else:
        print("usage:\n" + TOKEN_USAGE)


def run_command(command, args):
    client = LiffClient()
    if command == "token" or command == "t":
        if len(args) < 1:
            print("usage:\n" + TOKEN_USAGE)
            return
        subcommand = args[0]
        try:
            args = args[1:]
        except IndexError:
            args = []

        run_token_command(client, subcommand, args)

    elif command == "list" or command == "l":
        client.list_all_apps()

    elif command == "create" or command == "c":
        if len(args) < 2:
            print("usage:\n" + LIFF_APP_USAGE)
            return

        client.create_app(url=args[0], size=args[1])

    elif command == "delete" or command == "d":
        if len(args) < 1:
            print("usage:\n" + LIFF_APP_USAGE)
            return
        client.delete_app(args[0])

    elif command == "update" or command == "u":
        if len(args) < 2:
            print("usage:\n" + LIFF_APP_USAGE)
            return

        client.update_app(liff_id=args[0], properties=args[1])
    else:
        print(ALL_USAGE)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(ALL_USAGE)
        sys.exit(1)

    run_command(sys.argv[1], sys.argv[2:])

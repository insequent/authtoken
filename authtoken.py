#!/usr/bin/python3

# Script to automate getting an auth token from Rackspace's identity servers.

import http.client as http
import json, argparse
from getpass import getpass
from sys import stderr

def requestAuth(username, password, host="identity.api.rackspacecloud.com", pathPrefix="/v2.0"):
	requestData = makeRequestData(username, password)
	requestHeaders = {"Content-Type": "application/json"}

	connection = http.HTTPSConnection(host)
	connection.request("POST", pathPrefix + "/tokens", body=requestData, headers=requestHeaders)
	response = connection.getresponse()

	if response.status != http.OK:
		raise Exception("Error: server returned response code "+str(response.status)+": "+response.reason)

	return json.loads(response.read().decode())


def makeRequestData(username, password):
	data = {
		"auth": {
			"passwordCredentials": {
				"username": username, 
				"password": password
			}
		}
	}

	return json.dumps(data)

def jsonPrettify(jsonObj):
	return json.dumps(jsonObj, sort_keys=True, indent=4, separators=(',', ': '))

## main: ##

try:
	argParser = argparse.ArgumentParser(description="Gets an auth token.")
	argParser.add_argument("-u", "--username", default=argparse.SUPPRESS)
	argParser.add_argument("-p", "--password", default=argparse.SUPPRESS)
	argParser.add_argument("--host", default="identity.api.rackspacecloud.com")
	argParser.add_argument("-r", "--printRoles", default=False, action="store_const", const=True,
						   help="print the user roles in addition to the token id")
	argParser.add_argument("--printResponse", default=False, action="store_const", const=True,
						   help="print the entire response rather than just the token id")
	args = argParser.parse_args()

	if "username" not in args:
		args.username = input("username: ")
	if "password" not in args:
		args.password = getpass("password: ")

	print(args)
	authResponse = requestAuth(args.username, args.password, host=args.host);

	if args.printResponse:
		print(jsonPrettify(authResponse))
	else:
		try:
			print("token id: ", authResponse["access"]["token"]["id"])
			
			if args.printRoles:
				print("roles: ")
				for role in authResponse["access"]["user"]["roles"]:
					print("    {description} (name={name},id={id})".format(**role))

		except KeyError, TypeError:
			print("Error: unexpected JSON structure; could not find token id or roles", file=stderr)
			print("Recieved response:", file=stderr)
			print(jsonPrettify(authResponse), file=stderr)

except Exception as e:
	print(e)
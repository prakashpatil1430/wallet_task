from django.contrib.auth.backends import ModelBackend
import hashlib
import base64
import uuid
import random
import string
from rest_framework.authtoken.models import Token

from wallet_service.models import *


def generate_random_ids():
	return uuid.uuid1()


def generate_random_string():
	return ''.join(random.choices(string.ascii_uppercase+string.digits, k=8))


# fetch auth token of any user
def get_authentication_token(userid):
	user = Admins.objects.get(pk=userid)
	token, created = Token.objects.get_or_create(user=user)
	if created:
		token_key = created.key
	else:
		token_key = token.key
	return token_key


# to fetch errors wrt to each field
def get_json_errors(error_list_data):
	__field_errors = {}

	field_errors = [(k, v[0]) for k, v in error_list_data.items()]

	for key, error_list in field_errors:
		__field_errors[key] = error_list

	return __field_errors


def encode_str(text):
	string = str(text)
	encode = base64.b64encode(string.encode('ascii'))
	return str(encode.decode('ascii'))


def decode_str(encrypt_text):
	# string = str(encrypt_text)
	decode = base64.b64decode(encrypt_text).decode('ascii')
	return decode

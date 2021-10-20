from django.test import TestCase
import json
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from wallet_service.models import *
from wallet_service.views import *
from wallet_service.urls import *

# Create your tests here.


class WalletServiceAPIViewTestCase(APITestCase):

	def setUp(self):
		self.username = "mega9dsasas-8acb-19eb-zdfd-34e12d2604d511"
		cust_id = Customers.objects.create(customer_id=self.username)
		admin_id = Admins.objects.create(
										username=self.username,
										customer_id=cust_id.id)
		u = Admins.objects.get(username=self.username)
		authtoken = Token.objects.get_or_create(user=u)
		get_token = Token.objects.filter(user_id=u.id).first()
		self.token = get_token.key

	def api_authentication(self):
		self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)

	def test_wallet_withdraw_service(self):
		print("")
		print("")
		print("==================== Wallet Service =================")
		print("")

		# create a wallet
		url1 = reverse('wallet_details')

		data = {}

		response = self.client.post(
			url1,
			data,
			format='json',
			HTTP_AUTHORIZATION='Token ' + self.token)

		if response.status_code == 200:
			self.assertEqual(response.status_code, 200)

		# deposit amount in wallet
		url2 = reverse('wallet_deposit')
		amount = 5.0
		reference_id = 'qqh9ddac-8acb-19esasfdfd-3jdda2d2604d5'

		data = {
				'amount': amount,
				'reference_id': reference_id
		}

		response = self.client.post(
			url2,
			data,
			format='json',
			HTTP_AUTHORIZATION='Token ' + self.token)

		if response.status_code == 200:
			self.assertEqual(response.status_code, 200)

		# withdraw amount from wallet
		amount = 5.0
		reference_id = 'ddad-32432as-dsaadasda-1133'
		# reference_id = 'qqh9ddac-8acb-19esasfdfd-3jdda2d2604d5'

		data = {
				'amount': amount,
				'reference_id': reference_id
		}

		url = reverse('wallet_withdraw')

		print("Provided Data:\n")
		print(data)

		response = self.client.post(
			url,
			data,
			format='json',
			HTTP_AUTHORIZATION='Token ' + self.token)

		if response.status_code == 200:
			self.assertEqual(response.status_code, 200)

		get_response = (json.loads(response.content.decode('utf8')))

		print("\nResult:\n")
		print(get_response)

		print("\nStatus Code:\n\n"+str(response.status_code))

from django.shortcuts import render

from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework import permissions
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, logout
import datetime
from datetime import datetime as dt

from .models import *
from .serializers import *
from .common_functions import *

# Create your views here.


class UserLogin(GenericAPIView):
	"""
	Account Initialization for wallet
	"""
	serializer_class = UserLoginSerializers
	permission_classes = [
		permissions.AllowAny
	]

	@classmethod
	def post(self, request):
		response = {}
		user = {}

		postData = UserLoginSerializers(data=request.data)

		if postData.is_valid():

			customer_xid = postData.data['customer_id']

			check_customer_exists = Customers.objects.filter(
															customer_id=customer_xid).first()
			if not check_customer_exists:
				customer_id = Customers.objects.create(customer_id=customer_xid)
				user_rec = Admins.objects.create(
											customer=customer_id,
											username=customer_xid
										)
			else:
				customer_id = check_customer_exists
				user_rec = Admins.objects.filter(customer=customer_id).first()
			print(user_rec)
			token, _ = Token.objects.get_or_create(user=user_rec)

			if user_rec.id:
				user['customer_id'] = user_rec.customer_id

				response['data'] = user
				response['token'] = token.key
				response['status'] = 1
				return Response(res)
			else:
				response['errors'] = {"_error":'Customer not found'}
				response['status'] = 0
				return Response(res)

		else:
			response['errors'] = get_json_errors(postData.errors)
			response['status'] = 0
			return Response(response)


class EnableWallet(GenericAPIView):
	"""
	This Functionality is used to enable a wallet against a customer
	"""
	serializer_class = WalletDetailsSerializers

	@classmethod
	def post(self, request):
		res = {}
		post_data = WalletDetailsSerializers(data=request.data)
		if post_data.is_valid():

			findCustomer = Customers.objects.filter(id=request.user.customer_id).first()

			wallet_exists = WalletDetails.objects.filter(
														user_id=findCustomer.id).exists()
			if not wallet_exists:
				WalletDetails.objects.create(
											user_id=findCustomer.id,
											owned_by=findCustomer.customer_id,
											wallet_status=True,
											enabled_at=dt.now()
										)
			else:
				WalletDetails.objects.filter(
											user_id=findCustomer.id).update(wallet_status=True)

			wallet_details = WalletDetails.objects.filter(
															user_id=findCustomer.id).first()
			data = WalletDetailsSerializers(wallet_details).data
			basic = {}
			basic['id'] = encode_str(data['id'])
			basic['owned_by'] = data['owned_by']
			if data['wallet_status']:
				basic['wallet_status'] = "enabled"
			else:
				basic['wallet_status'] = "disabled"

			basic['balance'] = data['amount']
			basic['enabled_at'] = data['enabled_at']

			res['data'] = basic
			res["status_code"] = 1
			return Response(res)
		else:
			res['error_message'] = post_data.errors
			res["status_code"] = 0
			return Response(res)

	@classmethod
	def get(self, request):
		res = {}

		post_data = WalletDetailsSerializers(data=request.data)
		if post_data.is_valid():
			basic = {}

			findUser = Customers.objects.filter(id=request.user.customer_id).first()

			check_wallet_status = WalletDetails.objects.filter(
																owned_by=findUser.customer_id).first().wallet_status
			if check_wallet_status:
				wallet_exists = WalletDetails.objects.filter(
															user_id=findUser.id, wallet_status=True).exists()
				if wallet_exists:
					wallet_details = WalletDetails.objects.filter(user_id=findUser.id).first()
					data = WalletDetailsSerializers(wallet_details).data

					basic['id'] = encode_str(data['id'])
					basic['owned_by'] = data['owned_by']
					if data['wallet_status']:
						basic['wallet_status'] = "enabled"
					else:
						basic['wallet_status'] = "disabled"

					basic['enabled_at'] = data['enabled_at']
					balance = 0
					check_transactions = WalletTransactions.objects.filter(
																			user_id=findUser.id).values(
																										'deposited_by', 'withdrawn_by', 'amount')
					for i in check_transactions:
						if i['deposited_by']:
							balance = balance + i['amount']
						else:
							balance = balance - i['amount']
					basic['balance'] = balance
				res['data'] = basic
				res["status_code"] = 1
				return Response(res)
			else:
				res['error_message'] = 'Please enable your wallet to check balance amount!'
				res["status_code"] = 0
				return Response(res)
		else:
			res['error_message'] = post_data.errors
			res["status_code"] = 0
			return Response(res)

	@classmethod
	def patch(self, request):
		res = {}

		post_data = WalletDetailsSerializers(data=request.data)
		if post_data.is_valid():
			basic = {}

			findUser = Customers.objects.filter(id=request.user.customer_id).first()

			wallet_exists = WalletDetails.objects.filter(
															user_id=findUser.id, wallet_status=True).exists()
			if wallet_exists:
				WalletDetails.objects.filter(user_id=findUser.id).update(
																	wallet_status=False,
																	disabled_at=dt.now()
																)

				wallet_details = WalletDetails.objects.filter(user_id=findUser.id).first()
				data = WalletDetailsSerializers(wallet_details).data

				basic['id'] = encode_str(data['id'])
				basic['owned_by'] = data['owned_by']
				if data['wallet_status']:
					basic['wallet_status'] = "enabled"
				else:
					basic['wallet_status'] = "disabled"

				basic['disabled_at'] = data['disabled_at']

				balance = 0

				basic['balance'] = balance
			res['data'] = basic
			res["status_code"] = 1
			return Response(res)
		else:
			res['error_message'] = post_data.errors
			res["status_code"] = 0
			return Response(res)


class WalletDeposits(GenericAPIView):
	"""
	This Functionality is used to add money to a wallet
	"""
	serializer_class = WalletTransactionsSerializers

	@classmethod
	def post(self, request):
		res = {}

		post_data = WalletTransactionsSerializers(data=request.data)
		if post_data.is_valid():

			customer_id = request.user.customer_id
			print(customer_id)

			findUser = Customers.objects.filter(pk=customer_id).first()
			print(findUser)
			check_wallet_status = WalletDetails.objects.filter(
																owned_by=findUser.customer_id).first().wallet_status
			if check_wallet_status:

				# reference_id=generate_random_ids()
				reference_id = post_data.data.get('reference_id')

				wallet_exists = WalletDetails.objects.filter(
																user_id=findUser.id, wallet_status=True).first()
				if wallet_exists:
					WalletTransactions.objects.create(
												user_id=findUser.id,
												wallet_id=wallet_exists.id,
												reference_id=reference_id,
												amount=post_data.data.get('amount'),
												deposited_at=dt.now(),
												deposited_by=findUser.customer_id
											)

				wallet_details = WalletTransactions.objects.filter(
																	user_id=findUser.id, reference_id=reference_id).first()
				data = WalletTransactionsSerializers(wallet_details).data

				basic = {}
				basic['id'] = encode_str(data['id'])
				basic['reference_id'] = data['reference_id']
				basic['amount'] = data['amount']
				basic['deposited_by'] = data['deposited_by']
				basic['deposited_at'] = data['deposited_at']

				res['data'] = basic
				res["status_code"] = 1
				return Response(res)
			else:
				res['error_message'] = 'Please enable your wallet to check balance amount!'
				res["status_code"] = 0
				return Response(res)
		else:
			res['error_message'] = post_data.errors
			res["status_code"] = 0
			return Response(res)


class WalletWithdrawals(GenericAPIView):
	"""
	This Functionality is used to withdraw money from a wallet
	"""
	serializer_class = WalletTransactionsSerializers

	@classmethod
	def post(self, request):
		res = {}

		post_data = WalletTransactionsSerializers(data=request.data)
		if post_data.is_valid():

			customer_id = request.user.customer_id

			findUser = Customers.objects.filter(id=customer_id).first()
			check_wallet_status = WalletDetails.objects.filter(
																owned_by=findUser.customer_id).first().wallet_status
			if check_wallet_status:

				balance = 0
				check_transactions = WalletTransactions.objects.filter(
																		user_id=customer_id).values(
																									'deposited_by', 'withdrawn_by', 'amount')
				for i in check_transactions:
					if i['deposited_by']:
						balance = balance + i['amount']
					else:
						balance = balance - i['amount']

				if balance >= post_data.data.get('amount'):

					# reference_id=generate_random_ids()
					reference_id = post_data.data.get('reference_id')
					wallet_exists = WalletDetails.objects.filter(
																user_id=findUser.id, wallet_status=True).first()
					if wallet_exists:
						WalletTransactions.objects.create(
													user_id=findUser.id,
													wallet_id=wallet_exists.id,
													reference_id=reference_id,
													amount=post_data.data.get('amount'),
													withdrawn_at=dt.now(),
													withdrawn_by=findUser.customer_id
												)

					wallet_details = WalletTransactions.objects.filter(
																		user_id=findUser.id, reference_id=reference_id).first()
					data = WalletTransactionsSerializers(wallet_details).data

					basic = {}
					basic['id'] = encode_str(data['id'])
					basic['reference_id'] = data['reference_id']
					basic['amount'] = data['amount']
					basic['withdrawn_by'] = data['withdrawn_by']
					basic['withdrawn_at'] = data['withdrawn_at']

					res['data'] = basic
					res["status_code"] = 1
					return Response(res)
				else:
					res['error_message'] = 'The amount you are trying to withdraw is more than the balance you currently hold!'
					res["status_code"] = 0
					return Response(res)
			else:
				res['error_message'] = 'Please enable your wallet to check balance amount!'
				res["status_code"] = 0
				return Response(res)

		else:
			res['error_message'] = post_data.errors
			res["status_code"] = 0

			return Response(res)

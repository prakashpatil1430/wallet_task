from datetime import datetime as dt
from rest_framework import serializers
from django.db.models import Q

from .models import *
from .common_functions import *


class UserLoginSerializers(serializers.ModelSerializer):

	class Meta:
		model = Customers
		fields = '__all__'


class WalletDetailsSerializers(serializers.ModelSerializer):

	class Meta:
		model = WalletDetails
		fields = '__all__'


class WalletTransactionsSerializers(serializers.ModelSerializer):

	@classmethod
	def validate(self, data):
		errors = {}

		amount = data.get('amount')

		if not amount or amount == 0:
			errors['amount'] = "Amount should be greater than 0!"

		reference_id = data.get('reference_id')
		check_duplicate = WalletTransactions.objects.filter(
															reference_id=reference_id).exists()
		if check_duplicate:
			errors['reference_id'] = 'Duplicate Transaction Reference id. Please check'

		if errors:
			raise serializers.ValidationError(errors)

		return super(WalletTransactionsSerializers, self).validate(self, data)

	class Meta:
		model = WalletTransactions
		fields = '__all__'

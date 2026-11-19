from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import User, Company, Storage
from .services import create_company_for_user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"


class CompanyCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ("title", "inn")

    def create(self, validated_data):
        return create_company_for_user(user=self.context["request"].user, **validated_data)


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ("id", "title", "inn")


class StorageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Storage
        fields = ("id", "address", "company")
        read_only_fields = ("company",)
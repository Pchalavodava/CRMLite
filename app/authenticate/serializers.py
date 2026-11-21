from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import User, Company, Storage, Supplier, Product, Supply, SupplyProduct
from .services import create_company_for_user, create_supplier_for_company


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("id", "email", "password")

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class AttachUserToCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id",)

    def validate(self, data):
        user = self.instance

        if user.company_id is not None:
            raise serializers.ValidationError(f"This user already belongs to {user.company.title} company")

        return data

    def update(self, user, validated_data):
        company = self.context["request"].user.company

        user.company = company
        user.save(update_fields=["company"])

        return user


# __________________________________Company___________________________________________
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


# __________________________________Storage_______________________________________

class StorageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Storage
        fields = ("id", "address", "company")
        read_only_fields = ("company",)


# ______________________Supplier___________________________

class SupplierCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = ("title", "inn")

    def create(self, validated_data):
        return create_supplier_for_company(user=self.context["request"].user, **validated_data)


class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = ("id", "company", "title", "inn")
        read_only_fields = ("id", "company")


# ____________________________Product________________________________
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        # fields = "__all__"
        fields = ("title", "purchase_price", "sale_price", "storage", "quantity")
        read_only_fields = ("quantity",)

    def validate_storage(self, storage):
        user = self.context["request"].user

        if user.company_id != storage.company_id:
            raise serializers.ValidationError("You do not have access to this storage")

        return storage

    def create(self, validated_data):
        validated_data["quantity"] = 0

        return super().create(validated_data)


# ____________________________Supply________________________________

class SupplyProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupplyProduct
        fields = ("product", "quantity")

    def validate_quantity(self, quantity):
        if quantity <= 0:
            raise serializers.ValidationError("Quantity can not be less than 1")

        return quantity

    def validate_product(self, product):
        user = self.context["request"].user

        if user.company_id != product.storage.company_id:
            raise serializers.ValidationError("You do not have access to this product")

        return product


class SupplySerializer(serializers.ModelSerializer):
    products = SupplyProductSerializer(many=True, allow_empty=False)

    class Meta:
        model = Supply
        fields = ("supplier", "products")

    def validate_supplier(self, supplier):
        user = self.context["request"].user

        if user.company_id != supplier.company_id:
            raise serializers.ValidationError("You do not have access to this supplier")

        return supplier

    def validate_products(self, products):
        product_ids = [item["product"].id for item in products]

        if len(product_ids) != len(set(product_ids)):
            raise serializers.ValidationError("The same product cannot be added more than once")

        return products

    def create(self, validated_data):
        products_data = validated_data.pop("products")

        supply = Supply.objects.create(**validated_data)

        for item in products_data:
            product = item["product"]
            quantity = item["quantity"]

            SupplyProduct.objects.create(supply=supply, product=product, quantity=quantity)

            product.quantity += quantity
            product.save(update_fields=["quantity"])

        return supply


class SupplyProductListSerializer(serializers.ModelSerializer):
    product_title = serializers.CharField(source="product.title", read_only=True)

    class Meta:
        model = SupplyProduct
        # fields = ("product", "product_title", "quantity")
        fields = ("product_title", "quantity")


class SupplyListSerializer(serializers.ModelSerializer):
    supplier_title = serializers.CharField(source="supplier.title", read_only=True)
    products = SupplyProductListSerializer(source="supply_products", many=True, read_only=True)
    delivery_date = serializers.DateTimeField(format="%d.%m.%Y %H:%M", read_only=True)

    class Meta:
        model = Supply
        # fields = ("id", "supplier", "supplier_title", "delivery_date", "products")
        fields = ("id", "supplier_title", "delivery_date", "products")

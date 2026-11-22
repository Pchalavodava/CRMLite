import datetime

from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import ProtectedError
from django.shortcuts import render
from drf_spectacular.utils import extend_schema, OpenApiRequest
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAdminUser, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer, \
    TokenBlacklistSerializer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenBlacklistView

from .serializers import UserSerializer, CompanyCreateSerializer, CompanySerializer, StorageSerializer, \
    SupplierCreateSerializer, SupplierSerializer, ProductSerializer, SupplySerializer, SupplyListSerializer, \
    AttachUserToCompanySerializer, SaleCreateSerializer
from rest_framework.permissions import IsAuthenticated
from .permissions import HasCompanyPermission
from .models import Company, Storage, Supplier, Product, Supply

User = get_user_model()


@extend_schema(
    description="Create a new user endpoint",
    summary="Create a new user",
    tags=["Users"],
    # request=UserSerializer
    request=OpenApiRequest(
        request={
            "type": "object",
            "properties": {
                "password": {
                    "type": "string",
                    "example": "12345678"
                },
                "email": {
                    "type": "string",
                    "example": "example@example.com"
                },
                "is_active": {
                    "type": "boolean",
                    "example": True
                },
                "last_login": {
                    "type": "date-time",
                    "example": datetime.datetime.now()
                }
            }
        }
    )
)
class CreateUserView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    description="Delete user from the CRM system",
    summary="Delete user by ID",
    tags=["Users"],
    request=None,
    responses={204: None}
)
class DeleteUserView(APIView):
    permission_classes = [IsAdminUser]

    def delete(self, request, id):
        user = get_object_or_404(User, pk=id)
        user.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(
    description="Get user from CRM system",
    summary="Get user by ID",
    tags=["Users"],
    request=None,
    responses={200: UserSerializer, 404: None}
)
class GetUserView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, id):
        user = get_object_or_404(User, pk=id)
        serializer = UserSerializer(user)

        return Response(serializer.data)


@extend_schema(
    description='Enter by login and password',
    summary='Get access and refresh token',
    tags=['Authentication'],
    request=TokenObtainPairSerializer,
)
class LoginView(TokenObtainPairView):
    pass


@extend_schema(
    description='Generate a new access token using a refresh token',
    summary='Refresh token',
    tags=['Authentication'],
    request=TokenRefreshSerializer,
)
class RefreshView(TokenRefreshView):
    pass


@extend_schema(
    description='Blacklist the refresh token and log out the user',
    summary='Block refresh token',
    tags=['Authentication'],
    request=TokenBlacklistSerializer,
)
class LogoutView(TokenBlacklistView):
    pass


@extend_schema(
    description="Create a company and become its owner",
    summary="Create a company",
    tags=["Companies"],
    request=CompanyCreateSerializer,
    responses={201: CompanyCreateSerializer}
)
class CreateCompanyView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CompanyCreateSerializer(data=request.data, context={"request": request})

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)


@extend_schema(
    description="Get company by ID",
    summary="Get company",
    tags=["Companies"],
    responses={200: CompanySerializer}
)
class GetCompanyView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        company = get_object_or_404(Company, pk=id)

        serializer = CompanySerializer(company)

        return Response(serializer.data)


@extend_schema(
    description="Update company details",
    summary="Update company details",
    tags=["Companies"],
    request=CompanySerializer,
    responses={200: CompanySerializer}
)
class UpdateCompanyView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, id):
        company = get_object_or_404(Company, pk=id)

        if request.user.company_id != company.id or not request.user.is_company_owner:
            return Response({"detail": f"Only the company owner can update {company.title} company"},
                            status=status.HTTP_403_FORBIDDEN)

        serializer = CompanySerializer(company, data=request.data, partial=True)

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)


@extend_schema(
    description="Delete company",
    summary="Delete company",
    tags=["Companies"],
    request=None,
    responses={204: None, 403: None, 404: None}
)
class DeleteCompanyView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, id):
        company = get_object_or_404(Company, pk=id)

        if request.user.company_id != company.id or not request.user.is_company_owner:
            return Response({"detail": f"Only the company owner can delete {company.title} company"},
                            status=status.HTTP_403_FORBIDDEN)

        company.users.filter(is_company_owner=True).update(is_company_owner=False)

        company.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(
    summary="Attach user to company",
    description="Attach user to company",
    tags=["Companies"],
    responses={200: None, 404: None, 403: None, 400: None}
)
class AttachUserToCompanyView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        if not request.user.is_company_owner or not request.user.company_id:
            return Response({"detail": "Only company owner can attach users"}, status=status.HTTP_403_FORBIDDEN)

        user = get_object_or_404(User, pk=user_id)

        serializer = AttachUserToCompanySerializer(user, data={}, context={"request": request})

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {"message": "User successfully attached to your company", "user_id": user.id,
             "company_id": user.company_id}, status=status.HTTP_200_OK)


@extend_schema(
    description="Create storage",
    summary="Create storage",
    tags=["Storages"],
    request=StorageSerializer,
    responses={201: StorageSerializer}
)
class CreateStorageView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        if user.company_id is None or not user.is_company_owner:
            return Response({"detail": "Only company owner can create storage"},
                            status=status.HTTP_403_FORBIDDEN)

        serializer = StorageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(company=user.company)

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )


@extend_schema(
    description="Get all storages",
    summary="Get all storages",
    tags=["Storages"],
    responses={200: StorageSerializer(many=True)}
)
class GetStorageView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        storages = Storage.objects.filter(company_id=request.user.company_id)

        serializer = StorageSerializer(storages, many=True)

        return Response(serializer.data)


@extend_schema(
    description="Update storage",
    summary="Update storage",
    tags=["Storages"],
    request=StorageSerializer,
    responses={200: StorageSerializer}
)
class UpdateStorageView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, id):
        storage = get_object_or_404(Storage, pk=id)

        if request.user.company_id != storage.company_id or not request.user.is_company_owner:
            return Response({"detail": "Only company owner can update this storage"},
                            status=status.HTTP_403_FORBIDDEN)

        serializer = StorageSerializer(storage, data=request.data, partial=True)

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)


@extend_schema(
    description="Delete storage",
    summary="Delete storage",
    tags=["Storages"],
    request=None,
    responses={204: None, 403: None, 404: None}
)
class DeleteStorageView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, id):
        storage = get_object_or_404(Storage, pk=id)

        if request.user.company_id != storage.company_id or not request.user.is_company_owner:
            return Response({"detail": "Only company owner can delete this storage"},
                            status=status.HTTP_403_FORBIDDEN)

        storage.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


# ______________________Supplier___________________________
@extend_schema(
    description="Create supplier for company",
    summary="Create supplier",
    tags=["Suppliers"],
    request=SupplierCreateSerializer,
    responses={201: SupplierSerializer}
)
class CreateSupplierView(APIView):
    permission_classes = [IsAuthenticated, HasCompanyPermission]

    def post(self, request):
        serializer = SupplierCreateSerializer(data=request.data, context={"request": request})

        serializer.is_valid(raise_exception=True)
        supplier = serializer.save()

        return Response(SupplierSerializer(supplier).data, status=status.HTTP_201_CREATED)


@extend_schema(
    description="Get suppliers by user",
    summary="Get suppliers",
    tags=["Suppliers"],
    responses={200: SupplierSerializer(many=True)}
)
class GetSuppliersView(APIView):
    permission_classes = [IsAuthenticated, HasCompanyPermission]

    def get(self, request):
        company_id = request.user.company_id
        suppliers = Supplier.objects.filter(company_id=company_id)

        serializer = SupplierSerializer(suppliers, many=True)

        return Response(serializer.data)


@extend_schema(
    description="Update supplier details",
    summary="Update supplier details",
    tags=["Suppliers"],
    request=SupplierSerializer,
    responses={200: SupplierSerializer}
)
class UpdateSupplierView(APIView):
    permission_classes = [IsAuthenticated, HasCompanyPermission]

    def patch(self, request, id):
        supplier = get_object_or_404(Supplier, pk=id, company_id=request.user.company_id)

        serializer = SupplierSerializer(supplier, data=request.data, partial=True)

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)


@extend_schema(
    description="Delete supplier",
    summary="Delete supplier",
    tags=["Suppliers"],
    request=None,
    responses={204: None, 403: None, 404: None}
)
class DeleteSupplierView(APIView):
    permission_classes = [IsAuthenticated, HasCompanyPermission]

    def delete(self, request, id):
        supplier = get_object_or_404(Supplier, pk=id, company_id=request.user.company_id)

        try:
            supplier.delete()
        except ProtectedError:
            return Response({"detail": "You can't delete supplier, who participates in the supply"},
                            status=status.HTTP_409_CONFLICT)

        return Response(status=status.HTTP_204_NO_CONTENT)


# ______________________Product___________________________
@extend_schema(
    description="Get products",
    summary="Get products",
    tags=["Products"],
    responses={200: ProductSerializer(many=True), 403: None}
)
class GetProductListView(APIView):
    permission_classes = [IsAuthenticated, HasCompanyPermission]

    def get(self, request):
        products = Product.objects.filter(storage__company_id=request.user.company_id)

        serializer = ProductSerializer(products, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    description="Create product",
    summary="Create product",
    tags=["Products"],
    request=ProductSerializer,
    responses={201: ProductSerializer, 400: None, 403: None}
)
class CreateProductView(APIView):
    permission_classes = [IsAuthenticated, HasCompanyPermission]

    def post(self, request):
        serializer = ProductSerializer(data=request.data, context={"request": request})

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)


@extend_schema(
    description="Get product",
    summary="Get product",
    tags=["Products"],
    responses={200: ProductSerializer, 403: None, 404: None}
)
class GetProductView(APIView):
    permission_classes = [IsAuthenticated, HasCompanyPermission]

    def get(self, request, id):
        product = get_object_or_404(Product, pk=id, storage__company_id=request.user.company_id)

        serializer = ProductSerializer(product)

        return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    description="Update product",
    summary="Update product",
    tags=["Products"],
    request=ProductSerializer,
    responses={200: ProductSerializer, 400: None, 403: None, 404: None}
)
class UpdateProductView(APIView):
    permission_classes = [IsAuthenticated, HasCompanyPermission]

    def patch(self, request, id):
        product = get_object_or_404(Product, pk=id, storage__company_id=request.user.company_id)

        serializer = ProductSerializer(product, data=request.data, partial=True, context={"request": request})

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    description="Delete product",
    summary="Delete product",
    tags=["Products"],
    request=None,
    responses={204: None, 403: None, 404: None}
)
class DeleteProductView(APIView):
    permission_classes = [IsAuthenticated, HasCompanyPermission]

    def delete(self, request, id):
        product = get_object_or_404(Product, pk=id, storage__company_id=request.user.company_id)

        try:
            product.delete()
        except ProtectedError:
            return Response({"detail": "You can't delete the product, which used in supplies"},
                            status=status.HTTP_409_CONFLICT)

        return Response(status=status.HTTP_204_NO_CONTENT)


# ______________________Supply___________________________

@extend_schema(
    summary="Create supply",
    description="Create a supply and increase product quantities",
    tags=["Supplies"],
    request=SupplySerializer,
)
class CreateSupplyView(APIView):
    permission_classes = [IsAuthenticated, HasCompanyPermission]

    @transaction.atomic
    def post(self, request):
        serializer = SupplySerializer(data=request.data, context={"request": request})

        serializer.is_valid(raise_exception=True)
        supply = serializer.save()

        return Response({"message": "Supply created successfully", "supply_id": supply.id},
                        status=status.HTTP_201_CREATED)


@extend_schema(
    summary="Get supplies",
    description="Get supplies",
    tags=["Supplies"],
    responses={200: SupplyListSerializer(many=True)}
)
class SupplyListView(APIView):
    permission_classes = [IsAuthenticated, HasCompanyPermission]

    def get(self, request):
        supplies = Supply.objects.filter(supplier__company_id=request.user.company_id).select_related(
            "supplier").prefetch_related("supply_products__product")

        serializer = SupplyListSerializer(supplies, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


# ______________________________Sale___________________________________
@extend_schema(
    summary="Create sale",
    description="Create sale",
    tags=["Sales"],
    request=SaleCreateSerializer,
    responses={201: SaleCreateSerializer}
)
class CreateSaleView(APIView):
    permission_classes = [IsAuthenticated, HasCompanyPermission]

    @transaction.atomic
    def post(self, request):
        serializer = SaleCreateSerializer(data=request.data, context={"request": request})

        serializer.is_valid(raise_exception=True)

        serializer.save(company=request.user.company)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

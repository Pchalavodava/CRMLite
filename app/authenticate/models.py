from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.db.models import Q
from django.utils import timezone


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True")

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True")

        return self.create_user(email, password=password, **extra_fields)


# ______________________Company___________________________

class Company(models.Model):
    title = models.CharField(verbose_name="Company name", max_length=100)
    inn = models.CharField(unique=True, verbose_name="Taxpayer personal identification number", max_length=20)

    class Meta:
        verbose_name = "Company"
        verbose_name_plural = "Companies"

    def __str__(self):
        return self.title


# ______________________Supplier___________________________
class Supplier(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="suppliers")
    title = models.CharField(verbose_name="Supplier name", max_length=100)
    inn = models.CharField(verbose_name="Taxpayer personal identification number", max_length=20)

    class Meta:
        verbose_name = "Supplier"
        verbose_name_plural = "Suppliers"

        constraints = [models.UniqueConstraint(fields=["company", "inn"], name="unique_supplier_inn_per_company")]

    def __str__(self):
        return self.title


# _________________________Supply______________________
class Supply(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, related_name="supplies", db_column="supplier_id")
    delivery_date = models.DateTimeField(default=timezone.now)
    products = models.ManyToManyField("Product", through="SupplyProduct", related_name="supplies")

    class Meta:
        verbose_name = "Supply"
        verbose_name_plural = "Supplies"
        ordering = ["delivery_date"]

    def __str__(self):
        return f"Supply {self.pk} - {self.delivery_date}"


# __________________Storage_________________________

class Storage(models.Model):
    address = models.CharField(verbose_name="Company address", max_length=200)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="storages")

    class Meta:
        verbose_name = "Storage"
        verbose_name_plural = "Storages"

    def __str__(self):
        return f"{self.company} - storage address {self.address}"


# __________________________Product_______________________
class Product(models.Model):
    title = models.CharField(verbose_name="Product name", max_length=50)
    purchase_price = models.DecimalField(max_digits=8, decimal_places=2)
    sale_price = models.DecimalField(max_digits=8, decimal_places=2)
    quantity = models.PositiveIntegerField(default=0)
    storage = models.ForeignKey(Storage, on_delete=models.PROTECT, related_name="products")

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"
        # Здесь
        constraints = [
            models.CheckConstraint(condition=Q(purchase_price__gt=0), name="product_purchase_price_gt_zero"),
            models.CheckConstraint(condition=Q(sale_price__gt=0), name="product_sale_price_gt_zero")]

    def __str__(self):
        return f"{self.title} - purchase prise {self.purchase_price}"


# __________________________Supply product_______________________
class SupplyProduct(models.Model):
    supply = models.ForeignKey(Supply, on_delete=models.PROTECT, related_name="supply_products")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="product_ids")
    quantity = models.PositiveIntegerField()

    class Meta:
        verbose_name = "Supply product"
        verbose_name_plural = "Supply products"

        constraints = [
            models.UniqueConstraint(fields=["supply", "product"], name="unique_product_per_supply"),
            models.CheckConstraint(condition=Q(quantity__gt=0), name="supply_product_quantity_gt_zero")
        ]

    def __str__(self):
        return f"Product {self.product} - quantity {self.quantity}"


# _______________________________Sale_______________________________
class Sale(models.Model):
    buyer_name = models.CharField(verbose_name="Buyer name", max_length=50)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="company_sales")
    sale_date = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = "Sale"
        verbose_name_plural = "Sales"

    def __str__(self):
        return f"Date {self.sale_date}, buyer - {self.buyer_name}"


# _______________________________ProductSale_______________________________
class ProductSale(models.Model):
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="product_sales")
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name="product_sales")
    quantity = models.PositiveIntegerField()

    # Здесь
    sale_price = models.DecimalField(max_digits=8, decimal_places=2)
    purchase_price = models.DecimalField(max_digits=8, decimal_places=2)

    class Meta:
        verbose_name = "Product sale"
        verbose_name_plural = "Product sales"

        # Здесь
        constraints = [models.CheckConstraint(condition=Q(quantity__gt=0), name="product_sale_quantity_gt_zero"),
                       models.CheckConstraint(condition=Q(sale_price__gt=0), name="product_sale_sale_price_gt_zero"),
                       models.CheckConstraint(condition=Q(purchase_price__gt=0),
                                              name="product_sale_purchase_price_gt_zero")]

    def __str__(self):
        return f"Product {self.product.title}, quantity {self.quantity}"


# ____________________User_____________________

class User(AbstractUser):
    # username = None
    username = models.CharField(unique=True, null=True, blank=True, verbose_name="User name", max_length=150)
    email = models.EmailField(unique=True, verbose_name="Email address", max_length=255)

    company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, blank=True, related_name="users")
    is_company_owner = models.BooleanField(default=False, verbose_name="Is company owner")

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

        constraints = [
            models.UniqueConstraint(
                fields=["company"],
                condition=Q(is_company_owner=True),
                name="unique_company_owner"
            )
        ]

    def __str__(self):
        return self.email

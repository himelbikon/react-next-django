from django.db import models
from django.contrib.auth.models import AbstractUser, AbstractBaseUser
from django.contrib.auth.base_user import BaseUserManager


def printer(x):
    s = '---------------------------------'
    print(s)
    print(x)
    print(s)


class UserManager(BaseUserManager):
    def create_user(self, email, password=None):
        if not email:
            raise valueError('User must have an email!')
        if not password:
            raise valueError('User must have an password!')

        user = self.model(
            email=self.normalize_email(email)
        )
        user.set_password(password)
        user.is_admin = False
        user.is_ambassador = False
        user.is_staff = False
        user.is_superuser = False
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None):
        if not email:
            raise valueError('User must have an email!')
        if not password:
            raise valueError('User must have an password!')

        user = self.model(
            email=self.normalize_email(email)
        )
        user.set_password(password)
        user.is_admin = True
        user.is_ambassador = False
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractUser):
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(max_length=60, unique=True)
    password = models.CharField(max_length=255)
    is_ambassador = models.BooleanField(default=True)
    username = models.CharField(max_length=255, null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()


class Product(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(max_length=1900, null=True)
    image = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)


class Link(models.Model):
    code = models.CharField(max_length=255, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)


class Order(models.Model):
    transaction_id = models.CharField(max_length=255, null=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    code = models.CharField(max_length=255)
    ambassador_email = models.CharField(max_length=255)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    address = models.CharField(max_length=255, null=True)
    city = models.CharField(max_length=255, null=True)
    country = models.CharField(max_length=255, null=True)
    zip = models.CharField(max_length=255, null=True)
    complete = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name='order_items')
    product_title = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=20, decimal_places=2)
    quantity = models.IntegerField()
    admin_revenue = models.DecimalField(max_digits=20, decimal_places=2)
    ambassador_revenue = models.DecimalField(max_digits=20, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
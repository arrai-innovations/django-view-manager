from django.db import models
from django.db.models.fields import related


class Products(models.Model):
    name = models.CharField(max_length=1024)
    price = models.DecimalField(decimal_places=2, max_digits=9)
    markup_percentage = models.IntegerField()

    class Meta:
        ordering = ("name",)
        default_related_name = "products"

    def __str__(self):
        return f"{self.name} is a product."


class ProductCalculations(models.Model):
    product = related.OneToOneField("store.Products", on_delete=models.DO_NOTHING)
    markup_price = models.DecimalField(decimal_places=2, max_digits=9)
    markup_amount = models.DecimalField(decimal_places=2, max_digits=9)

    class Meta:
        managed = False
        db_table = "store_productcalculations"
        default_related_name = "calculations"

    def __str__(self):
        return f"{self.sale_price} is the sale price."


class PurchasedProducts(models.Model):
    product = models.OneToOneField("store.Products", on_delete=models.PROTECT)
    quantity = models.IntegerField()

    class Meta:
        ordering = ("product__name",)
        default_related_name = "order_items"

    def __str__(self):
        return f"{self.order_number} is an order."


class PurchasedProductCalculations(models.Model):
    purchased_product = models.OneToOneField("store.PurchasedProducts", on_delete=models.PROTECT)
    profit = models.DecimalField(decimal_places=2, max_digits=9)

    class Meta:
        managed = False
        db_table = "store_purchasedproductcalculations"
        default_related_name = "calculations"

    def __str__(self):
        return f"{self.profit} is the profit."

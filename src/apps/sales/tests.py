from decimal import Decimal

from django.contrib.auth.models import User
from django.urls import reverse
from django.test import TestCase

from apps.inventory.models import Product
from apps.sales.models import Sale
from apps.sales.services import (
	InsufficientStockError,
	add_product_to_sale,
	change_sale_item_quantity,
)


class SaleStockTests(TestCase):
	def setUp(self):
		self.user = User.objects.create_user(username="seller")
		self.product = Product.objects.create(
			barcode="123",
			description="Produto teste",
			cust=Decimal("5.00"),
			price=Decimal("10.00"),
			quantity=2,
		)
		self.sale = Sale.objects.create(seller=self.user)

	def test_adding_product_decreases_stock(self):
		sale, sale_item = add_product_to_sale(self.sale.pk, self.product.barcode)

		self.product.refresh_from_db()
		self.assertEqual(self.product.quantity, 1)
		self.assertEqual(sale_item.quantity, 1)
		self.assertEqual(sale.total_quantity, 1)

	def test_summary_update_persists_and_returns_json(self):
		self.client.force_login(self.user)

		response = self.client.post(
			reverse("sales:update_sale_summary", args=[self.sale.pk]),
			{
				"client": "Cliente teste",
				"status": Sale.Status.PAID,
				"payment_method": Sale.PaymentMethod.CASH,
				"discount": "1.00",
				"freight": "2.00",
				"cash_received": "11.00",
			},
		)

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.json()["sale"]["total_price"], "R$ 1,00")
		self.sale.refresh_from_db()
		self.assertEqual(self.sale.client, "Cliente teste")
		self.assertEqual(self.sale.status, Sale.Status.PAID)

	def test_new_sale_reuses_empty_draft(self):
		self.client.force_login(self.user)

		first_response = self.client.get(reverse("sales:new_sale"))
		second_response = self.client.get(reverse("sales:new_sale"))

		self.assertEqual(first_response.context["sale"].pk, second_response.context["sale"].pk)
		self.assertEqual(Sale.objects.filter(seller=self.user).count(), 1)

	def test_cannot_add_product_without_stock(self):
		self.product.quantity = 0
		self.product.save(update_fields=["quantity"])

		with self.assertRaises(InsufficientStockError):
			add_product_to_sale(self.sale.pk, self.product.barcode)

		self.assertFalse(self.sale.sale_items.exists())

	def test_changing_sale_quantity_keeps_stock_in_sync(self):
		_, sale_item = add_product_to_sale(self.sale.pk, self.product.barcode)

		change_sale_item_quantity(self.sale.pk, sale_item.pk, 1)
		self.product.refresh_from_db()
		self.assertEqual(self.product.quantity, 0)

		change_sale_item_quantity(self.sale.pk, sale_item.pk, -1)
		self.product.refresh_from_db()
		self.assertEqual(self.product.quantity, 1)

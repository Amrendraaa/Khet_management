# Copyright (c) 2025, amrendra and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _


class StockTransaction(Document):
	def validate(self):
		if not self.item or not self.quantity:
			frappe.throw(_(" Item and Quantity are required."))
		if self.quantity <= 0:
			frappe.throw(_("Quantity must be greater than zero."))
		
	def on_submit(self):
		self.update_stock()

	def update_stock(self):
		item = frappe.get_doc("Inventory Item", self.item)

		if self.type == "In":
			item.current_stock += self.quantity
		elif self.type == "Out":
			if self.quantity > item.current_stock:
				frappe.throw(_("Now enough stock to perform this transaction. Available: {0}, Required: {1}").format(item.current_stock, self.quantity))
			item.current_stock -= self.quantity

		item.save()

		frappe.msgprint(_("Stock updated for Item: {0}. New Stock: {1}").format(item.item_name, item.current_stock))

		self.check_and_create_purchase_request(item)
	
	def check_and_create_purchase_request(self, item):
		if item.current_stock < item.default_reorder_level:
			farm = frappe.get_doc("Farm", self.farm)
			existing = frappe.db.exists("Purchase Request", {
				"item": item.name,
				"farm": self.farm,
				"requested_by": farm.owner_of_farm,
				"status": "Draft",
				"is_supplier_assigned": 0
			})
			if not existing:
				
				pr = frappe.new_doc("Purchase Request")
				pr.item = item.name
				pr.quantity = item.default_reorder_level * 2
				pr.required_by = frappe.utils.add_days(frappe.utils.nowdate(), 5)
				pr.farm = self.farm
				pr.status = "Draft"
				pr.requested_by = farm.owner_of_farm
				pr.is_supplier_assigned = 0
				pr.insert(ignore_permissions=True)
				frappe.msgprint(_("Auto created purchase request {0}").format(pr.name))
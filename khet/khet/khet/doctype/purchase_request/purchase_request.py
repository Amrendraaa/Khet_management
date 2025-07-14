# Copyright (c) 2025, amrendra and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _


class PurchaseRequest(Document):
	def validate(self):
		if self.quantity <= 0:
			frappe.throw(_("Quantity must be greater than 0"))

	def before_submit(self):
		if not self.supplier:
			frappe.throw(_("Supplier must be assigned before submitting the Purchase Request."))



@frappe.whitelist()
def fulfill_request(pr_name):
	pr = frappe.get_doc("Purchase Request", pr_name)

	if pr.docstatus != 0:
		frappe.throw("Only Draft Purchase Request can be fulfilled.")

	if not pr.supplier:
		frappe.throw("Supplier must be assigned before fulfilling the request.")

	invoice = frappe.new_doc("Supplier Invoice")
	invoice.purchase_request = pr.name
	invoice.supplier = pr.supplier
	invoice.invoice_date = frappe.utils.nowdate()
	invoice.payment_status = "Pending"

	rate = get_supplier_rate(pr.supplier, pr.item)
	invoice.append("items", {
		"item": pr.item,
		"quantity": pr.quantity,
		"rate": rate,
		"amount": pr.quantity * rate
	})

	invoice.insert(ignore_permissions=True)

	pr.status = "Fulfilled"
	pr.save()

	return invoice.name


def get_supplier_rate(supplier, item):
	result = frappe.db.get_value("Supplied Item", {
		"parent": supplier,
		"item": item
	}, "price_per_unit")
	return float(result or 0)


def suggest_supplier_for_item(item_name, farm_region):
	suppliers = frappe.get_all("Supplier", filters={"region": farm_region}, fields=["name"])
	for sup in suppliers:
		supplied_items = frappe.get_all("Supplied Item", filters={
			"parent": sup.name,
			"item": item_name
		})
		if supplied_items:
			return sup.name
	return None

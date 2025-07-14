# Copyright (c) 2025, amrendra and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class SupplierInvoice(Document):
	pass

@frappe.whitelist()
def mark_as_cleared(invoice_name):
    invoice = frappe.get_doc("Supplier Invoice", invoice_name)

    if invoice.payment_status == "Cleared":
        frappe.throw("Invoice is already cleared.")

    for row in invoice.items:
        item = frappe.get_doc("Inventory Item", row.item)
        item.current_stock += row.quantity
        item.save()

    invoice.payment_status = "Cleared"
    invoice.save()

    return "Stock updated and invoice cleared."


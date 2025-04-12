# Copyright (c) 2025, Aerele and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.desk.form.linked_with import get_linked_doctypes

class SDWorkerWageClass(Document):
	def before_validate(self):
		if not self.is_new():
			employees_list = frappe.db.sql(
				f"""
					SELECT name FROM `tabEmployee` WHERE sd_worker_wage_class = '{self.name}' 
					AND sd_minimum_wages < {self.sd_minimum_wages}
				""", as_list=True
			)
			emp_list = []
			if employees_list:
				for emp in employees_list:
					emp_list.append(emp[0])
				employees = "<br> ".join(emp_list)
				frappe.throw(f"These employees shift wages less than {self.sd_minimum_wages} <br><br> {employees}")
			else:
				frappe.db.sql(
					f"""
						UPDATE `tabEmployee` SET sd_minimum_wages = {self.sd_minimum_wages} WHERE sd_worker_wage_class = '{self.name}'
					"""
				)

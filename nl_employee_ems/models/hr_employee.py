import requests
from collections import defaultdict
from odoo import models, fields, api


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    expense_line_ids = fields.One2many(
        'employee.expense', 'employee_id', string="Expense Lines")

    expense_total_by_currency = fields.Html(compute='_compute_total_by_currency')


    @api.depends('expense_line_ids.amount', 'expense_line_ids.currency_id')
    def _compute_total_by_currency(self):
        print('Triggered Compute Total By Currency')
        totals = self.compute_total_by_currency().items()
        for record in self:
            record.expense_total_by_currency = '<br/>'.join(
                [f'{currency.name} - Total: {currency.symbol} {amount}' for currency, amount in totals])
            print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
            print([f'{currency.name} - Total: {currency.symbol} {amount}' for currency, amount in totals])
            print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
            

    def compute_total_by_currency(self):
        totals_by_currency = defaultdict(float)
        for record in self.expense_line_ids.filtered(lambda r: r.state == 'approved'):
            totals_by_currency[record.currency_id] += record.amount
        return totals_by_currency
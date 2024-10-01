import requests
from collections import defaultdict
from odoo import models, fields, api


class EmployeeExpense(models.Model):
    _name = 'employee.expense'
    _description = """
    expense management module in Odoo, which includes employee expense submission, 
    approval workflows, integration with an external currency conversion API, and automated reporting.
    """

    employee_id = fields.Many2one('hr.employee', 'Employee', required=True)
    description = fields.Text('Expense Discrption')
    currency_id = fields.Many2one('res.currency', 'Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id)
    company_currency_id = fields.Many2one(
        'res.currency', 'Company Currency', default=lambda self: self.env.user.company_id.currency_id, store=True)
    amount = fields.Float(
        'Amount', currency_field='currency_id', required=True)
    converted_amount = fields.Float(
        compute='_compute_converted_amount', store=True, currency_field='company_currency_id')
    state = fields.Selection(selection=[
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], default='draft')
    receipt = fields.Binary('Receipt Scan')
    receipt_filename = fields.Char('Receipt Filename')
    date = fields.Date('Submission Date',
                       default=lambda self: fields.Date.today())
    approval_date = fields.Date()
    approved_by = fields.Many2one('res.users')
    hide_submit = fields.Boolean(compute='_compute_hide_submit')
    total_by_currency = fields.Html(compute='_compute_total_by_currency')
    hide_total_currency = fields.Boolean(compute="_compute_hide_total_currency")



    @api.depends('state')
    def _compute_hide_total_currency(self):
        totals = self.compute_total_by_currency().items()
        print('>>>>>>>>>>>>>>>>>>')
        print(totals)
        print('>>>>>>>>>>>>>>>>>>')
        for record in self:
            record.hide_total_currency = len(totals) <= 0
            

    @api.depends('amount', 'currency_id', 'state')
    def _compute_total_by_currency(self):
        totals = self.compute_total_by_currency().items()
        for record in self:
            record.total_by_currency = '<br/>'.join(
                [f'{currency.name} - Total: {currency.symbol} {amount}' for currency, amount in totals])

    def compute_total_by_currency(self):
        totals_by_currency = defaultdict(float)
        for record in self.search([('state', '=', 'approved')]):
            totals_by_currency[record.currency_id] += record.amount
        return totals_by_currency

    @api.depends('state')
    def _compute_hide_submit(self):
        for record in self:
            record.hide_submit = self.env.user.has_group('hr.group_hr_manager')

    @api.depends('employee_id')
    def _compute_display_name(self):
        for record in self:
            record.display_name = f'{record.employee_id.name} - Expense'

    @api.depends('amount', 'currency_id')
    def _compute_converted_amount(self):

        company_currency = self.env.user.company_id.currency_id
        for record in self:
            print('Copmany Currency:', record.company_currency_id.name,
                  'Record Currency:', record.currency_id.name)
            if record.currency_id != company_currency:
                record.converted_amount = record._get_conversion_rate(
                    record.amount, record.currency_id, company_currency)
            else:
                record.converted_amount = record.amount

    def _get_conversion_rate(self, amount, from_currency, to_currency):

        if amount == 0:
            return amount

        api_url = 'https://api.exchangerate-api.com/v4/latest/{}'.format(
            from_currency.name)
        response = requests.get(api_url)
        if response.status_code == 200:
            data = response.json()
            rate = data['rates'].get(to_currency.name, 1)
            return amount * rate
        return amount

    # Logic for buttons' actions

    def action_submit(self):
        self.state = 'submitted'

    def action_approve(self):
        self.state = 'approved'
        self.approval_date = fields.Date.today()
        self.approved_by = self.env.user

    def action_reject(self):
        self.state = 'rejected'

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

class Bank(models.Model):
    _name = 'cash.control.bank'
    _description = 'Cuenta Bancaria'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Banco", required=True, tracking=True,)
    movement_ids = fields.One2many('cash.control.bank.movement', 'bank_id', string='Movimientos bancarios')
    current_balance = fields.Float(string="Saldo actual", compute="_compute_current_balance", store=True, tracking=True, help="Suma de todos los movimientos de la cuenta bancaria.")

    @api.depends('movement_ids', 'movement_ids.signed_amount')
    def _compute_current_balance(self):
        for bank in self:
            bank.current_balance = sum(m.signed_amount for m in bank.movement_ids)

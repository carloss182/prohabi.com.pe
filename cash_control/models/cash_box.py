from odoo import models, fields, api

class CashBox(models.Model):
    _name = 'cash.control.box'
    _description = 'Caja de Efectivo'
    _inherit = ['mail.thread', 'mail.activity.mixin']  # <-- Se heredan los mixins

    name = fields.Char(
        string='Nombre de la caja',
        required=True,
        tracking=True  # Para que aparezca en el chatter si se modifica
    )

    movement_ids = fields.One2many(
        'cash.control.movement',
        'box_id',
        string='Movimientos'
    )

    current_balance = fields.Float(
        string='Saldo actual',
        compute='_compute_current_balance',
        store=True,
        help='Suma de todos los ingresos/egresos de la caja.',
        tracking=True  # Para hacer tracking de cambios
    )

    @api.depends('movement_ids', 'movement_ids.signed_amount')
    def _compute_current_balance(self):
        for record in self:
            record.current_balance = sum(m.signed_amount for m in record.movement_ids)

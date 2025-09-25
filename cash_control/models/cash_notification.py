from odoo import models, fields

class CashControlNotification(models.Model):
    _name = 'cash.control.notification'
    _description = 'Notificaciones para movimientos de caja'

    name = fields.Char(
        string='Nombre',
        required=True,
        help='Un nombre descriptivo para esta notificación.'
    )
    user_id = fields.Many2one(
        'res.users',
        string='Usuario a notificar',
        required=True,
        help='Usuario al que se enviará correo cuando se cree un movimiento.'
    )
    active = fields.Boolean(
        string='Activo',
        default=True,
        help='Desmarca esta casilla para deshabilitar la notificación.'
    )

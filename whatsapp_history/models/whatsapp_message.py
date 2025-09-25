from odoo import models, fields

class WhatsappMessage(models.Model):
    _name = 'whatsapp.message'
    _description = 'Historial de WhatsApp'
    _order = 'date desc'

    partner_id = fields.Many2one('res.partner', string='Contacto', required=True)
    message = fields.Text(string='Mensaje', required=True)
    direction = fields.Selection([('incoming', 'Entrante'), ('outgoing', 'Saliente')], string='Dirección', required=True)
    date = fields.Datetime(string='Fecha', required=True, default=fields.Datetime.now())

    # ❌ COMENTAR ESTE CAMPO TEMPORALMENTE PARA PROBAR
    # mail_message_id = fields.Many2one('mail.message', string="Mensaje Relacionado", ondelete="cascade")

from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    whatsapp_message_ids = fields.One2many('whatsapp.message', 'partner_id', string="Historial de WhatsApp")

    def action_view_whatsapp_history(self):
        return {
            'name': 'Historial de WhatsApp',
            'type': 'ir.actions.act_window',
            'res_model': 'whatsapp.message',
            'view_mode': 'tree,form',
            'domain': [('partner_id', '=', self.id)],
            'target': 'new'
        }

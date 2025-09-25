from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

class CashMovement(models.Model):
    _name = 'cash.control.movement'
    _description = 'Movimiento de Caja'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, id desc'

    name = fields.Char(string='Secuencia', copy=False, readonly=True, default=lambda self: _('Nuevo'), tracking=True)
    box_id = fields.Many2one('cash.control.box', string='Caja', required=True, ondelete='cascade', tracking=True)
    date = fields.Datetime(string='Fecha y hora', default=fields.Datetime.now, required=True, tracking=True)
    type = fields.Selection(
        [
            ('ingreso', 'Ingreso'),
            ('egreso', 'Egreso'),
            ('transferencia_banco', 'Transferencia a Banco')
        ], string='Tipo', required=True, tracking=True)
    amount = fields.Float(string='Monto (+)', required=True, help='Monto en positivo. Si es egreso o transferencia a banco, se convertirá en negativo internamente.', tracking=True)
    signed_amount = fields.Float(string='Monto', compute='_compute_signed_amount', store=True)
    responsible_id = fields.Many2one('res.partner', required=True, string='Responsable')
    notes = fields.Text(string='Anotaciones', required=True, tracking=True)
    # Campos para rendición
    por_rendir = fields.Boolean(string='Por rendir', tracking=True, help='Si está marcado, se habilitan campos de rendición.')
    monto_rendido = fields.Float(string='Monto rendido', tracking=True, help='Valor que ha sido rendido de este movimiento.', default=0.0)
    fecha_rendicion = fields.Date(string='Fecha de rendición', tracking=True)
    rendicion_state = fields.Selection(
        [
            ('no_aplica', 'No aplica'),
            ('sin_rendir', 'Sin rendir'),
            ('parcial', 'Parcial'),
            ('rendido', 'Rendido')
        ], string='Estado de rendición', compute='_compute_rendicion_state', store=True, default='no_aplica', tracking=True)
    # Nuevo campo para definir el banco destino cuando se realice una transferencia desde caja
    target_bank_id = fields.Many2one('cash.control.bank', string='Banco Destino', help="Banco al que se transfiere el monto. Solo se debe definir si el tipo es 'Transferencia a Banco'.")
    is_transferencia_banco = fields.Boolean(string="Es transferencia a banco", compute="_compute_transfer_flags", store=True,)
    box_balance = fields.Float(string='Balance de la Caja', compute='_compute_box_balance', store=False,)

    @api.depends('box_id')
    def _compute_box_balance(self):
        """Calcula el balance de la caja. Si no hay movimientos, el balance es 0.0."""
        for rec in self:
            rec.box_balance = rec.box_id.current_balance if rec.box_id else 0.0

    @api.depends('type')
    def _compute_transfer_flags(self):
        """Determina si el movimiento es una transferencia a banco."""
        for rec in self:
            rec.is_transferencia_banco = (rec.type == 'transferencia_banco')

    @api.depends('type', 'amount')
    def _compute_signed_amount(self):
        """Calcula el monto firmado basado en el tipo de movimiento."""
        for record in self:
            if record.type in ['egreso', 'transferencia_banco']:
                record.signed_amount = -abs(record.amount or 0.0)
            else:
                record.signed_amount = abs(record.amount or 0.0)

    @api.depends('por_rendir', 'amount', 'monto_rendido')
    def _compute_rendicion_state(self):
        """Calcula el estado de rendición basado en el monto rendido y el monto total."""
        for record in self:
            if not record.por_rendir:
                record.rendicion_state = 'no_aplica'
            else:
                if record.monto_rendido == 0:
                    record.rendicion_state = 'sin_rendir'
                elif 0 < record.monto_rendido < record.amount:
                    record.rendicion_state = 'parcial'
                elif record.monto_rendido == record.amount:
                    record.rendicion_state = 'rendido'
                else:
                    record.rendicion_state = 'parcial'

    @api.constrains('type', 'amount')
    def _check_amount_sign(self):
        """Valida que el monto sea positivo y que el monto firmado sea correcto según el tipo de movimiento."""
        for record in self:
            if record.amount < 0:
                raise ValidationError(_("El campo 'Monto (+)' debe ser positivo."))
            # Para egreso y transferencia a banco, el monto firmado debe ser negativo.
            if record.type in ['egreso', 'transferencia_banco'] and record.signed_amount > 0:
                raise ValidationError(_("Para egreso y transferencia a banco, el monto firmado debe ser negativo."))
            # Para ingreso, el monto firmado debe ser positivo.
            if record.type == 'ingreso' and record.signed_amount < 0:
                raise ValidationError(_("Para ingreso, el monto firmado no puede ser negativo."))

    @api.constrains('target_bank_id', 'type')
    def _check_target_bank(self):
        """Valida que se seleccione un banco destino solo para movimientos de tipo 'Transferencia a Banco'."""
        for record in self:
            if record.type == 'transferencia_banco' and not record.target_bank_id:
                raise ValidationError(_("Para movimientos de tipo 'Transferencia a Banco' se debe seleccionar un Banco Destino."))
            if record.type != 'transferencia_banco' and record.target_bank_id:
                raise ValidationError(_("Solo los movimientos de tipo 'Transferencia a Banco' pueden tener asignado un Banco Destino."))

    @api.constrains('monto_rendido', 'amount', 'por_rendir')
    def _check_monto_rendido(self):
        """Valida que el monto rendido no exceda el monto otorgado."""
        for record in self:
            if record.por_rendir and record.monto_rendido > record.amount:
                raise ValidationError(_(
                    "El Monto Rendido (%.2f) no puede exceder al Monto Otorgado (%.2f)."
                ) % (record.monto_rendido, record.amount))

    @api.model
    def create(self, vals):
        """Crea un nuevo movimiento de caja y envía notificaciones por correo."""
        if vals.get('name', _('Nuevo')) == _('Nuevo'):
            seq = self.env['ir.sequence'].next_by_code('cash.control.movement') or _('Nuevo')
            vals['name'] = seq
        rec = super(CashMovement, self).create(vals)
        
        # Notificaciones por correo
        notifications = self.env['cash.control.notification'].search([('active', '=', True)])
        if not notifications:
            raise UserError(_(
                "No se ha configurado ningún usuario para notificar por correo en el módulo de Notificaciones. "
                "Por favor, configure al menos un usuario para notificaciones."
            ))
        body_html = _(
            '<p>Se ha creado un nuevo movimiento <strong>{}</strong>.</p>'
            '<p><strong>Responsable:</strong> {}</p>'
            '<p><strong>Tipo:</strong> {}</p>'
            '<p><strong>Monto:</strong> {}</p>'
            '<p><strong>Notas:</strong> {}</p>'
        ).format(
            rec.name, rec.responsible_id.name, rec.type, rec.amount, rec.notes or ''
        )
        if rec.por_rendir:
            body_html += (
                '<p><strong>Por rendir:</strong> Sí</p>'
                '<p><strong>Monto rendido:</strong> {}</p>'
                '<p><strong>Fecha de rendición:</strong> {}</p>'
                '<p>Este es un mensaje automático generado desde el sistema. No responda a este mensaje.</p>'
            ).format(rec.monto_rendido, rec.fecha_rendicion or '')
        for notify in notifications:
            partner = notify.user_id.partner_id
            if partner.email:
                mail_values = {
                    'subject': _('Movimiento de efectivo: %s') % rec.name,
                    'body_html': body_html,
                    'email_to': partner.email,
                }
                mail = self.env['mail.mail'].create(mail_values)
                mail.send()
        
        # Lógica para transferencia a banco desde caja:
        # Al ser una transferencia, el movimiento en caja es un egreso y se debe crear un movimiento
        # en el banco destino (modelo cash.control.bank.movement) con tipo 'ingreso'
        if rec.type == 'transferencia_banco' and rec.target_bank_id:
            self.env['cash.control.bank.movement'].create({
                'name': rec.name,
                'bank_id': rec.target_bank_id.id,
                'date': rec.date,
                'type': 'ingreso',
                'amount': rec.amount,
                'responsible_id': rec.responsible_id.id,
                'notes': _("Transferencia recibida desde Caja %s") % rec.box_id.name,
            })
        return rec
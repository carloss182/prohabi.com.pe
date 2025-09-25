from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

class BankMovement(models.Model):
    _name = 'cash.control.bank.movement'
    _description = 'Movimiento Bancario'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, id desc'

    name = fields.Char(string='Secuencia', copy=False, readonly=True, default=lambda self: _('Nuevo'), tracking=True,)
    bank_id = fields.Many2one('cash.control.bank', string='Banco', required=True, ondelete='cascade', tracking=True,)
    date = fields.Datetime(string='Fecha y hora', default=fields.Datetime.now, required=True, tracking=True,)
    type = fields.Selection(
        [
            ('ingreso', 'Ingreso'),
            ('egreso', 'Egreso'),
            ('transferencia', 'Transferencia a Caja'),
            ('transferencia_banco', 'Transferencia a Banco'),
        ], string='Tipo', required=True, tracking=True,)
    amount = fields.Float(string='Monto (+)', required=True, help='Monto en positivo. Si es egreso o transferencia, se convertirá en negativo internamente.', tracking=True,)
    signed_amount = fields.Float(string='Monto', compute='_compute_signed_amount', store=True,)
    responsible_id = fields.Many2one('res.partner', string='Responsable', required=True,)
    notes = fields.Text(string='Anotaciones', required=True, tracking=True,)
    target_cash_box_id = fields.Many2one('cash.control.box', string='Caja Destino', help="Caja a la que se transfiere el monto. Solo se debe definir si el tipo es 'Transferencia a Caja'.")
    target_bank_id = fields.Many2one('cash.control.bank',string='Banco Destino', help="Banco a la que se transfiere el monto. Solo se debe definir si el tipo es 'Transferencia a Banco'.")
    origen = fields.Selection(
        [            
            ('pago', 'Pago'),
            ('devolucion', 'Devolución'),
            ('cambio_moneda', 'Cambio de Moneda'),
            ('prestamo', 'Préstamo'),
            ('transferencia_extranjero', 'Transferencia de Extranjero'),
        ],string='Origen', required=True, tracking=True)
    moneda = fields.Selection(
        [
            ('pen', 'PEN'),
            ('usd', 'USD'),
        ], string='Moneda', default='pen', tracking=True,)
    is_transferencia = fields.Boolean(string="Es transferencia a caja", compute="_compute_transfer_flags", store=True,)
    is_transferencia_banco = fields.Boolean(string="Es transferencia a banco", compute="_compute_transfer_flags", store=True,)
    balance = fields.Float(string='Balance', compute='_compute_balance', store=False,)

    @api.depends('bank_id')
    def _compute_balance(self):
        """Calcula el balance de banco. Si no hay movimientos, el balance es 0.0."""
        for rec in self:
            rec.balance = rec.bank_id.current_balance if rec.bank_id else 0.0

    @api.depends('type')
    def _compute_transfer_flags(self):
        for rec in self:
            rec.is_transferencia = rec.type == 'transferencia'
            rec.is_transferencia_banco = rec.type == 'transferencia_banco'

    @api.depends('type', 'amount')
    def _compute_signed_amount(self):
        for record in self:
            record.signed_amount = -abs(record.amount or 0.0) if record.type in ['egreso', 'transferencia', 'transferencia_banco'] else abs(record.amount or 0.0)

    @api.constrains('amount')
    def _check_amount_positive(self):
        for record in self:
            if record.amount < 0:
                raise ValidationError(_("El campo 'Monto (+)' debe ser positivo."))

    @api.constrains('type', 'target_cash_box_id', 'target_bank_id')
    def _check_target_transfer(self):
        for record in self:
            if record.type == 'transferencia' and not record.target_cash_box_id:
                raise ValidationError(_("Para movimientos de tipo 'Transferencia a Caja' se debe seleccionar una Caja Destino."))
            if record.type != 'transferencia' and record.target_cash_box_id:
                raise ValidationError(_("Solo los movimientos de tipo 'Transferencia a Caja' pueden tener asignada una Caja Destino."))
            if record.type == 'transferencia_banco' and not record.target_bank_id:
                raise ValidationError(_("Para movimientos de tipo 'Transferencia a Banco' se debe seleccionar un Banco Destino."))
            if record.type != 'transferencia_banco' and record.target_bank_id:
                raise ValidationError(_("Solo los movimientos de tipo 'Transferencia a Banco' pueden tener asignado un Banco Destino."))

    # @api.constrains('amount', 'type', 'bank_id')
    # def _check_sufficient_balance(self):
    #     for rec in self:
    #         if rec.type in ['egreso', 'transferencia', 'transferencia_banco'] and rec.bank_id.current_balance < rec.amount:
    #             raise ValidationError(_("Saldo insuficiente en la cuenta bancaria para realizar esta operación."))

    @api.model
    def create(self, vals):
        if vals.get('name', _('Nuevo')) == _('Nuevo'):
            vals['name'] = self.env['ir.sequence'].next_by_code('cash.control.bank.movement') or _('Nuevo')
        rec = super(BankMovement, self).create(vals)
        
        notifications = self.env['cash.control.notification'].search([('active', '=', True)])
        if not notifications:
            raise UserError(_("No se ha configurado ningún usuario para notificar por correo en el módulo de Notificaciones. Por favor, configure al menos un usuario para notificaciones."))
        
        body_html = _(
            '<p>Se ha creado un nuevo movimiento bancario <strong>{}</strong>.</p>'
            '<p><strong>Banco:</strong> {}</p>'
            '<p><strong>Responsable:</strong> {}</p>'
            '<p><strong>Tipo:</strong> {}</p>'
            '<p><strong>Monto:</strong> {}</p>'
            '<p><strong>Notas:</strong> {}</p>'
        ).format(
            rec.name,
            rec.bank_id.name,
            rec.responsible_id.name,
            rec.type,
            rec.amount,
            rec.notes or ''
        )
        if rec.type == 'transferencia' and rec.target_cash_box_id:
            body_html += _('<p><strong>Caja Destino:</strong> {}</p>').format(rec.target_cash_box_id.name)
        if rec.type == 'transferencia_banco' and rec.target_bank_id:
            body_html += _('<p><strong>Banco Destino:</strong> {}</p>').format(rec.target_bank_id.name)
        
        for notify in notifications:
            partner = notify.user_id.partner_id
            if partner.email:
                mail_values = {
                    'subject': _('Nuevo Movimiento Bancario: %s') % rec.name,
                    'body_html': body_html,
                    'email_to': partner.email,
                }
                self.env['mail.mail'].create(mail_values).send()
        
        if rec.type == 'transferencia' and rec.target_cash_box_id:
            self.env['cash.control.movement'].create({
                'name': rec.name,
                'box_id': rec.target_cash_box_id.id,
                'date': rec.date,
                'type': 'ingreso',
                'amount': rec.amount,
                'responsible_id': rec.responsible_id.id,
                'notes': _("Transferencia desde Banco %s") % rec.bank_id.name,
            })
        elif rec.type == 'transferencia_banco':
            if rec.target_bank_id.id == rec.bank_id.id:
                raise ValidationError(_("No se puede transferir al mismo banco."))
            if self.env['cash.control.bank'].search_count([('id', '!=', rec.bank_id.id)]) < 1:
                raise UserError(_("No se ha encontrado otro banco para realizar la transferencia."))
            self.env['cash.control.bank.movement'].create({
                'name': rec.name,
                'bank_id': rec.target_bank_id.id,
                'date': rec.date,
                'type': 'ingreso',
                'amount': rec.amount,
                'responsible_id': rec.responsible_id.id,
                'notes': _("Transferencia recibida desde Banco %s") % rec.bank_id.name,
            })
        return rec

    def write(self, vals):
        for rec in self:
            if rec.type in ['transferencia', 'transferencia_banco']:
                raise UserError(_("Para editar un movimiento de tipo 'Transferencia a Caja' o 'Transferencia a Banco', debe eliminar el registro anterior manualmente y crear uno nuevo."))
        return super(BankMovement, self).write(vals)
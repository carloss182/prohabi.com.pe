# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import fields, models, api
from odoo.exceptions import ValidationError


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    open_ai_model = fields.Char(
        string="ChatOpenAI Model",
        related="company_id.open_ai_model",
        readonly=False
    )
    open_ai_api_key = fields.Char(
        string="OpenAI API KEY",
        related="company_id.open_ai_api_key",
        readonly=False
    )
    open_ai_max_tokens = fields.Integer(
        string="OpenAI Max Tokens",
        related="company_id.open_ai_max_tokens",
        readonly=False,
        default=250
    )

    @api.constrains('open_ai_max_tokens')
    def _check_open_ai_max_tokens_field(self):
        for tokens in self:
            if tokens.open_ai_max_tokens < 150:
                raise ValidationError('The value of Open AI Max Tokens must be at least 150.')

# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    open_ai_model = fields.Char(
        string="ChatOpenAI Model")
    open_ai_api_key = fields.Char(
        string="OpenAI API KEY")
    open_ai_max_tokens = fields.Integer(
        string="OpenAI Max Tokens")
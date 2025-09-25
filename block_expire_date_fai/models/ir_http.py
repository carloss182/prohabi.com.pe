
from datetime import datetime, timedelta

from odoo import models


class IrHttpInherit(models.AbstractModel):
    _inherit='ir.http'

    def session_info(self):
        result = super(IrHttpInherit, self).session_info()
        ICP = self.env['ir.config_parameter'].sudo()
        create_date = ICP.get_param('database.create_date')
        create_date = datetime.strptime(create_date, "%Y-%m-%d %H:%M:%S")
        expiration_date = create_date + timedelta(days=90)
        result['warning'] = False
        result['expiration_date'] = str(expiration_date)
        return result
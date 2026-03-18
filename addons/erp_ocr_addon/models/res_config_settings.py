from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    azure_endpoint = fields.Char(
        string="Azure Endpoint",
        config_parameter="clario_ocr.azure_endpoint"
    )

    azure_api_key = fields.Char(
        string="Azure API Key",
        config_parameter="clario_ocr.azure_api_key"
    )
from odoo import models, fields, api

class GearGuardModel(models.Model):
    _name = 'gearguard.model'
    _description = 'GearGuard Model'

    name = fields.Char(string='Name', required=True)
    description = fields.Text(string='Description')

from odoo import models, fields, api

class GearGuardTeam(models.Model):
    _name = 'gearguard.team'
    _description = 'Maintenance Team'

    name = fields.Char(string='Name', required=True)

class GearGuardEquipment(models.Model):
    _name = 'gearguard.equipment'
    _description = 'Equipment'

    name = fields.Char(string='Name', required=True)
    serial_no = fields.Char(string='Serial No')
    team_id = fields.Many2one('gearguard.team', string='Team')
    department = fields.Char(string='Department')
    location = fields.Char(string='Location')
    is_usable = fields.Boolean(string='Is Usable', default=True)
    
    request_ids = fields.One2many('gearguard.request', 'equipment_id', string='Requests')
    request_count = fields.Integer(compute='_compute_request_count', string='Request Count')

    @api.depends('request_ids')
    def _compute_request_count(self):
        for record in self:
            record.request_count = len(record.request_ids)

    def action_view_requests(self):
        self.ensure_one()
        return {
            'name': 'Maintenance Requests',
            'type': 'ir.actions.act_window',
            'res_model': 'gearguard.request',
            'view_mode': 'tree,form',
            'domain': [('equipment_id', '=', self.id)],
            'context': {'default_equipment_id': self.id},
        }

class GearGuardRequest(models.Model):
    _name = 'gearguard.request'
    _description = 'Maintenance Request'

    name = fields.Char(string='Subject', required=True)
    equipment_id = fields.Many2one('gearguard.equipment', string='Equipment', required=True)
    technician_id = fields.Many2one('res.users', string='Technician')
    state = fields.Selection([
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('repaired', 'Repaired'),
        ('scrapped', 'Scrapped')
    ], string='Status', default='new', group_expand='_expand_states')
    request_type = fields.Selection([
        ('corrective', 'Corrective'),
        ('preventive', 'Preventive')
    ], string='Request Type', default='corrective')
    scheduled_date = fields.Datetime(string='Scheduled Date')
    duration = fields.Float(string='Duration (Hours)')

    def _expand_states(self, states, domain, order):
        return [key for key, val in type(self).state.selection]

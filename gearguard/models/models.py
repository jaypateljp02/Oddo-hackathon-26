from odoo import models, fields, api

class MaintenanceTeam(models.Model):
    _name = 'gearguard.team'
    _description = 'Maintenance Team'

    name = fields.Char(string='Team Name', required=True)
    # Link specific users (Technicians) to these teams [cite: 23]
    member_ids = fields.Many2many('res.users', string='Team Members')

class Equipment(models.Model):
    _name = 'gearguard.equipment'
    _description = 'Equipment Asset'

    name = fields.Char(string='Equipment Name', required=True)
    serial_no = fields.Char(string='Serial Number')
    # Tracking ownership and details [cite: 9]
    department = fields.Char(string='Department') 
    location = fields.Char(string='Location')
    # Default maintenance team [cite: 12]
    team_id = fields.Many2one('gearguard.team', string='Assigned Team')
    is_usable = fields.Boolean(string='Is Usable', default=True)
    
    # For the Smart Button Logic [cite: 71]
    request_count = fields.Integer(compute='_compute_request_count', string="Request Count")

    def _compute_request_count(self):
        for record in self:
            record.request_count = self.env['gearguard.request'].search_count([('equipment_id', '=', record.id)])

    def action_view_requests(self):
        # Clicking button opens list of requests related to that machine 
        return {
            'type': 'ir.actions.act_window',
            'name': 'Maintenance Requests',
            'res_model': 'gearguard.request',
            'view_mode': 'tree,form',
            'domain': [('equipment_id', '=', self.id)],
            'context': {'default_equipment_id': self.id},
        }

class MaintenanceRequest(models.Model):
    _name = 'gearguard.request'
    _description = 'Maintenance Request'
    _inherit = ['mail.thread', 'mail.activity.mixin'] # Adds chatter/logging if allowed

    name = fields.Char(string='Subject', required=True) # Subject: What is wrong? [cite: 31]
    equipment_id = fields.Many2one('gearguard.equipment', string='Equipment', required=True)
    # Request Types [cite: 27]
    request_type = fields.Selection([
        ('corrective', 'Corrective'),
        ('preventive', 'Preventive')
    ], string='Request Type', default='corrective')
    
    team_id = fields.Many2one('gearguard.team', string='Team')
    technician_id = fields.Many2one('res.users', string='Technician')
    scheduled_date = fields.Date(string='Scheduled Date')
    duration = fields.Float(string='Duration (Hours)')
    
    # Stages for Kanban [cite: 55]
    state = fields.Selection([
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('repaired', 'Repaired'),
        ('scrap', 'Scrap')
    ], string='Status', default='new', group_expand='_expand_states')

    # Auto-Fill Logic: Auto fetch team from equipment 
    @api.onchange('equipment_id')
    def _onchange_equipment_id(self):
        if self.equipment_id and self.equipment_id.team_id:
            self.team_id = self.equipment_id.team_id

    # Scrap Logic: Indicate equipment is no longer usable [cite: 76]
    def action_move_to_scrap(self):
        self.write({'state': 'scrap'})
        if self.equipment_id:
            self.equipment_id.is_usable = False
            
    # Required for Kanban drag and drop to show all columns
    def _expand_states(self, states, domain, order):
        return [key for key, val in type(self).state.selection]

from odoo import models, fields


class BookReport(models.Model):
    _name = 'lotes_viewv'
    _description = 'Lotes Report'
    _auto = False
    id = fields.Float(string='id')
    id_partner = fields.Many2one(comodel_name='res.partner', string='Proveedor')
    importe = fields.Float('Importe')

    def init(self):
        self.env.cr.execute("""
           CREATE OR REPLACE VIEW lotes_viewv AS
           (SELECT AVG(id) AS id,id_partner,sum(importe) as importe 
           FROM lotes 
           GROUP BY id_partner)
        """)


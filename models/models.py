from odoo import models, fields, api, Command, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class FixPosTest(models.Model):
    _inherit = 'account.payment'

    def _seek_for_lines(self):
        ''' Helper used to dispatch the journal items between:
        - The lines using the temporary liquidity account.
        - The lines using the counterpart account.
        - The lines being the write-off lines.
        :return: (liquidity_lines, counterpart_lines, writeoff_lines)
        '''
        self.ensure_one()
        _logger.warning("Ejecutando _seek_for_lines para el pago con ID: %s", self.id)
        # liquidity_lines, counterpart_lines, writeoff_lines
        lines = [self.env['account.move.line'] for _dummy in range(3)]
        valid_account_types = self._get_valid_payment_account_types()
        for line in self.move_id.line_ids:
            _logger.info("Procesando línea ID %s: Cuenta %s, Débito %s, Crédito %s", line.id, line.account_id.display_name, line.debit, line.credit)
            if line.account_id in self._get_valid_liquidity_accounts():
                if line.debit > 0:
                    lines[0] += line  # liquidity_lines
                elif line.credit > 0:
                    lines[1] += line  # counterpart_lines
            elif line.account_id.account_type in valid_account_types or line.account_id == line.company_id.transfer_account_id:
                if line.debit > 0:
                    lines[0] += line  # liquidity_lines
                elif line.credit > 0:
                    lines[1] += line  # counterpart_lines
            else:
                lines[2] += line  # writeoff_lines
        
        return lines

    
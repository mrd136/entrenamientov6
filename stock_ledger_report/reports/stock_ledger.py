from datetime import date, datetime

from dateutil.relativedelta import relativedelta
from odoo import models, api, _, _lt, fields
from odoo.osv import expression


class ReportStockLedger(models.AbstractModel):
    _inherit = 'account.report'
    _name = 'stock_ledger_report.stock.ledger'
    _description = "Stock Ledger"

    filter_date = {'mode': 'range', 'filter': 'today'}
    filter_warehouse = True
    filter_location = True
    filter_product = True
    filter_unfold_all = False

    @api.model
    def _init_filter_product(self, options, previous_options=None):
        if not self.filter_product:
            return

        options['product'] = True
        options['product_ids'] = previous_options and previous_options.get('product_ids') or []
        options['product_categories'] = previous_options and previous_options.get('product_categories') or []
        selected_product_ids = [int(partner) for partner in options['product_ids']]
        selected_product = selected_product_ids and self.env['product.product'].browse(selected_product_ids) or \
                           self.env[
                               'product.product']
        options['selected_product_ids'] = selected_product.mapped('name')
        selected_product_category_ids = [int(category) for category in options['product_categories']]
        selected_partner_categories = selected_product_category_ids and self.env['product.category'].browse(
            selected_product_category_ids) or self.env['product.category']
        options['selected_product_categories'] = selected_partner_categories.mapped('name')

    @api.model
    def _get_options_product_domain(self, options):
        domain = [('product_id.active', '=', True)]
        if options.get('product_ids'):
            product_ids = [int(product) for product in options['product_ids']]
            domain.append(('product_id', 'in', product_ids))
        if options.get('product_categories'):
            partner_product_ids = [int(category) for category in options['product_categories']]
            domain.append(('product_id.category_id', 'in', partner_product_ids))
        return domain

    @api.model
    def _get_filter_warehouse(self):
        return self.env['stock.warehouse'].search([
            ('company_id', 'in', self.env.user.company_ids.ids or [self.env.company.id])
        ], order="company_id, name")

    @api.model
    def _init_filter_warehouse(self, options, previous_options=None):
        if self.filter_warehouse is None:
            return

        if previous_options and previous_options.get('warehouse'):
            warehouse_map = dict((opt['id'], opt['selected']) for opt in previous_options['warehouse'] if
                                 opt['id'] != 'divider' and 'selected' in opt)
        else:
            warehouse_map = {}

        options['warehouse'] = []
        for j in self._get_filter_warehouse():
            locations = self.env['stock.location'].search([('location_id', '=', j.view_location_id.id)]).ids
            options['warehouse'].append({
                'id': j.id,
                'name': j.name,
                'code': j.code,
                'location_id': locations,
                'selected': warehouse_map.get(j.id, False)
            })

    @api.model
    def _get_options_warehouse(self, options):
        return [
            warehouse for warehouse in options.get('warehouse', []) if
            not warehouse['id'] in ('divider', 'group') and warehouse['selected']
        ]

    @api.model
    def _get_options_warehouse_domain(self, options):
        # Make sure to return an empty array when nothing selected to handle archived journals.
        selected_warehouse = self._get_options_warehouse(options)
        location_ids = []
        for warehouse in selected_warehouse:
            for location in warehouse['location_id']:
                location_ids.append(location)
        if options.get('dest', False):
            base = selected_warehouse and [('location_dest_id', 'in', location_ids)] or []
            for location in location_ids:
                expression.OR([base, ('location_dest_id', 'child_of', location)])
        else:
            base = selected_warehouse and [('location_id', 'in', location_ids)] or []
            for location in location_ids:
                expression.OR([base, ('location_id', 'child_of', location)])
        return base

    @api.model
    def _get_options_warehouse_ids(self, options):
        selected_warehouse = self._get_options_warehouse(options)
        return [j['id'] for j in selected_warehouse]

    @api.model
    def _get_filter_location(self):
        return self.env['stock.location'].search([
            ('company_id', 'in', self.env.user.company_ids.ids or [self.env.company.id])
        ], order="company_id, name")

    @api.model
    def _init_filter_location(self, options, previous_options=None):
        if self.filter_location is None:
            return
        view_locations = []
        if previous_options and previous_options.get('location'):
            location_map = dict((opt['id'], opt['selected']) for opt in previous_options['location'] if
                                opt['id'] != 'divider' and 'selected' in opt)
        else:
            location_map = {}

        options['location'] = []
        if previous_options and previous_options.get('warehouse'):
            view_locations = self.env['stock.warehouse'].browse(
                [warehouse['id'] for warehouse in previous_options.get('warehouse') if warehouse['selected']]).mapped(
                'view_location_id').ids
        if view_locations:
            locations = self.env['stock.location'].search(
                [('company_id', 'in', self.env.user.company_ids.ids or [self.env.company.id]),
                 ('location_id', 'in', view_locations)], order="company_id, name", )
            for j in locations:
                options['location'].append({
                    'id': j.id,
                    'name': j.name,
                    'selected': location_map.get(j.id, False)
                })

        else:
            for j in self._get_filter_location():
                options['location'].append({
                    'id': j.id,
                    'name': j.name,
                    'selected': location_map.get(j.id, False)
                })

    @api.model
    def _get_options_location(self, options):
        return [
            location for location in options.get('location', []) if
            not location['id'] in ('divider', 'group') and location['selected']
        ]

    @api.model
    def _get_options_location_domain(self, options):
        # Make sure to return an empty array when nothing selected to handle archived journals.
        selected_locations = self._get_options_location(options)
        location_ids = [j['id'] for j in selected_locations]
        if options.get('dest', False):
            base = selected_locations and [('location_dest_id', 'in', location_ids)] or []
            for location in location_ids:
                expression.OR([base, ('location_dest_id', 'child_of', location)])
        else:
            base = selected_locations and [('location_id', 'in', location_ids)] or []
            for location in location_ids:
                expression.OR([base, ('location_id', 'child_of', location)])
        return base

    @api.model
    def _get_options_location_ids(self, options):
        selected_location = self._get_options_location(options)
        return [j['id'] for j in selected_location]

    @api.model
    def _get_options_current_period(self, options):
        ''' Create options with the 'strict_range' enabled on the filter_date / filter_comparison.
        :param options: The report options.
        :return:        A copy of the options.
        '''
        new_options = options.copy()
        new_options['date'] = {
            'mode': 'range',
            'date_from': options['date']['date_from'],
            'date_to': options['date']['date_to'],
            'strict_range': options['date']['date_from'] is not False,
        }
        new_options['journals'] = []
        return new_options

    @api.model
    def _get_options_beginning_period(self, options):
        ''' Create options with the 'strict_range' enabled on the filter_date.
        :param options: The report options.
        :return:        A copy of the options.
        '''
        new_options = options.copy()
        date_tmp = fields.Date.from_string(options['date']['date_from']) - relativedelta(days=1)
        new_options['date'] = {
            'mode': 'single',
            'date_from': False,
            'date_to': fields.Date.to_string(date_tmp),
        }
        return new_options

    @api.model
    def _get_options_date_domain(self, options):
        if not options.get('date'):
            return []

        date_field = options['date'].get('date_field', 'date')

        if options['date']['filter'] == 'todayBis':
            domain = [(date_field, '<=', options['date']['date_to'] + ' 23:59:59')]
            domain += [(date_field, '>=', options['date']['date_to'] + ' 00:00:01')]
        else:
            domain = [(date_field, '<=', options['date']['date_to'])]
            domain += [(date_field, '>=', options['date']['date_from'])]
        return domain

    @api.model
    def _get_options_domain(self, options):
        domain = [('state', '=', 'done')]
        domain += self._get_options_warehouse_domain(options)
        domain += self._get_options_location_domain(options)
        domain += self._get_options_product_domain(options)
        domain += self._get_options_date_domain(options)
        return domain

    def _get_templates(self):
        return {
            'main_template': 'account_reports.main_template',
            'main_table_header_template': 'account_reports.main_table_header',
            'line_template': 'stock_ledger_report.line_template_stock_ledger_report',
            'footnotes_template': 'account_reports.footnotes_template',
            'search_template': 'stock_ledger_report.search_template',
        }

    def _get_report_name(self):
        return _('Stock Ledger')

    @api.model
    def _get_dates_period(self, options, date_from, date_to, mode, period_type=None, strict_range=False):
        res = super()._get_dates_period(options, date_from, date_to, mode, period_type=period_type,
                                        strict_range=strict_range)
        if res['period_type'] == 'today':
            res['string'] = 'Today'
        return res

    def _get_inventory_date(self, at_date, location, product):
        query = """
        SELECT SUM(COALESCE(q1.qty_in, 0) - COALESCE(q2.qty_out, 0)) AS total
        FROM (
            SELECT SUM(sml.qty_done) AS qty_in
            FROM stock_move AS sm
            INNER JOIN stock_move_line AS sml
            ON sml.move_id = sm.id
            WHERE sm.location_dest_id = %s AND 
                sm.date < %s AND 
                sm.product_id = %s AND
	            sm.state = 'done'
            ) AS q1,
            (SELECT SUM(sml.qty_done) AS qty_out
            FROM stock_move AS sm
            INNER JOIN stock_move_line AS sml
            ON sml.move_id = sm.id
            WHERE sm.location_id = %s AND 
                sm.date < %s AND 
                sm.product_id = %s AND
	            sm.state = 'done'
            ) AS q2
        """
        self.env.cr.execute(query, (location.id, at_date, product.id, location.id, at_date, product.id))
        res = self.env.cr.dictfetchall()
        return res[0].get('total')

    @api.model
    def _do_query(self, options, expanded_partner=None):
        options['dest'] = False
        d = {}
        from_ids = self.env['stock.move'].search(self._get_options_domain(options))
        # sm.picking_type_id, sm.name, sm.product_uom_qty, sm.date, sm.reference, sm.product_uom, sm.product_id
        query = """
                SELECT sm.location_id, sm.product_id, array_agg(sm.id) AS sm_ids
                FROM stock_move AS sm
                WHERE sm.id in %s
                GROUP BY sm.product_id, sm.location_id
                        """
        if from_ids:
            self.env.cr.execute(query, (tuple(from_ids.ids),))
            res = self.env.cr.dictfetchall()
            for line in res:
                if d.get(line.get('product_id'), False):
                    d.get(line.get('product_id')).append(line)
                else:
                    d[line.get('product_id')] = [line]
        options['dest'] = True
        to_ids = self.env['stock.move'].search(self._get_options_domain(options))
        query = """
                SELECT sm.location_dest_id, sm.product_id, array_agg(sm.id) AS sm_ids
                FROM stock_move AS sm
                WHERE sm.id in %s
                GROUP BY sm.product_id, sm.location_dest_id
                        """
        if to_ids:
            self.env.cr.execute(query, (tuple(to_ids.ids),))
            res = self.env.cr.dictfetchall()
            for line in res:
                if d.get(line.get('product_id'), False):
                    lines = d.get(line.get('product_id'))
                    for x in lines:
                        if x.get('location_id') == line.get('location_dest_id'):
                            x.get('sm_ids').extend(line.get('sm_ids'))
                            break
                    else:
                        lines.append(line)
                else:
                    d[line.get('product_id')] = [line]
        return d

    @api.model
    def _get_lines(self, options, line_id=None):
        d = self._do_query(options)
        if not d:
            return
        context = self.env.context
        unfold_all = context.get('print_mode') and not options.get('unfolded_lines') or options.get('partner_id')
        products = self.env['product.product'].search([])
        # warehouse_ids = self._get_options_warehouse_ids(options)
        # if warehouse_ids:
        #     inventory_to_date = {}
        #     for warehouse in warehouse_ids:
        #         temp = products.with_context(to_date=options['date']['date_to'], warehouse=warehouse)._product_available()
        #         for key, value in temp.items():
        #             if inventory_to_date.get(key, False):
        #                 inventory_to_date[key]['qty_available'] += value['qty_available']
        #             else:
        #                 inventory_to_date[key] = {'qty_available': value['qty_available']}
        # else:
        inventory_to_date = products.with_context(to_date=options['date']['date_to'])._product_available()
        result_lines = []
        for product_id, lines in d.items():
            product_id = self.env['product.product'].browse(product_id)
            result_lines.append({
                'id': 'product_' + str(product_id.id),
                'name': product_id.name,
                'columns': [],
                'level': 1,
                # 'trust': partner.trust,
                'unfoldable': True,
                'unfolded': 'product_' + str(product_id.id) in options.get('unfolded_lines') or unfold_all,
                'colspan': 6,
            })
            for location_line in lines:  # line == sm grouped by location
                moves = self.env['stock.move'].browse(location_line.get('sm_ids'))
                current_location = self.env['stock.location'].browse(location_line.get('location_id'))
                if not current_location:
                    current_location = self.env['stock.location'].browse(location_line.get('location_dest_id'))
                if current_location.usage not in ['internal']:
                    continue
                result_lines.append({
                    'id': 'location_' + str(current_location.id) + '_product_' + str(product_id.id),
                    'name': current_location.complete_name + ' as of ' + options['date']['date_from'],
                    'parent_id': 'product_' + str(product_id.id),
                    'columns': [{'name': v} for v in
                                [self._get_inventory_date(options['date']['date_from'], current_location, product_id)]],
                    'level': 3,
                    # 'trust': partner.trust,
                    'unfoldable': True,
                    'unfolded': 'location_' + str(current_location.id) + '_product_' + str(
                        product_id.id) in options.get('unfolded_lines') or unfold_all,
                    'colspan': 6,
                })
                # everything is [0] because of some weird add bug WTF
                for move in moves:
                    qty = move[0].quantity_done * -1 if move[0].location_dest_id.id != current_location.id else move[
                        0].quantity_done
                    columns = [
                        {'name': 'inventory adjustment' if not move[0].picking_type_id and move[0].inventory_id else move[0].picking_type_id.name},
                        {'name': move[0].picking_id.partner_id.name},
                        {'name': move[0].date},
                        {'name': move[0].reference},
                        {'name': move[0].name},
                        {'name': qty, 'class': 'number'},
                        {'name': move[0].product_uom.name},
                    ]
                    result_lines.append({
                        'id': move[0].id,
                        'caret_options': 'stock.move',
                        'name': move[0].name,  # format_date(self.env, aml['date']),
                        'parent_id': 'location_' + str(current_location.id) + '_product_' + str(product_id.id),
                        # 'class': 'date',
                        'columns': columns,
                        # 'caret_options': caret_type,
                        'level': 4,
                    })
                result_lines.append({
                    'id': 'location_' + str(current_location.id) + '_product_' + str(product_id.id) + '_last',
                    'name': current_location.complete_name + ' as of ' + options['date']['date_to'],
                    'parent_id': 'product_' + str(product_id.id),
                    'columns': [{'name': v} for v in
                                [self._get_inventory_date(options['date']['date_to'], current_location, product_id)]],
                    'level': 3,
                    # 'trust': partner.trust,
                    'unfoldable': False,
                    'colspan': 6,
                })
            result_lines.append({
                'id': 'product_' + str(product_id.id) + '_total',
                'name': 'Total as of ' + options['date']['date_to'],
                'parent_id': 'product_' + str(product_id.id),
                'columns': [{'name': v} for v in
                            [inventory_to_date[product_id.id]['qty_available']]],
                'level': 2,
                # 'trust': partner.trust,
                'unfoldable': False,
                'colspan': 6,
            })
        return result_lines

    def open_document(self, options, params=None):
        if not params:
            params = {}
        ctx = self.env.context.copy()
        ctx.pop('id', '')

        # Decode params
        model = params.get('model', 'stock.move')
        res_id = params.get('id')
        document = params.get('object', 'stock.move')

        # Redirection data
        target = self._resolve_caret_option_document(model, res_id, document)
        view_name = self._resolve_caret_option_view(target)
        module = 'stock'
        if '.' in view_name:
            module, view_name = view_name.split('.')

        # Redirect
        view_id = self.env['ir.model.data'].get_object_reference(module, view_name)[1]
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'views': [(view_id, 'form')],
            'res_model': document,
            'view_id': view_id,
            'res_id': target.id,
            'context': ctx,
        }

    @api.model
    def _resolve_caret_option_view(self, target):
        """Retrieve the target view name of the caret option.

        :param target:  The target record of the redirection.
        :return: The target view name as a string.
        """
        if target._name == 'stock.move':
            return 'stock.view_move_form'

    def _get_columns_name(self, options):
        columns = [
            {},
            {'name': _("Type"), 'class': 'string', 'style': 'white-space:nowrap;'},
            {'name': _("Contact"), 'class': 'string', 'style': 'white-space:nowrap;'},
            {'name': _("Date"), 'class': 'number', 'style': 'white-space:nowrap;'},
            {'name': _("Num"), 'class': 'number', 'style': 'white-space:nowrap;'},
            {'name': _("Memo"), 'class': 'string', 'style': 'white-space:nowrap;'},
            {'name': _("Qty"), 'class': 'number', 'style': 'white-space:nowrap;'},
            {'name': _("U/M"), 'class': 'string', 'style': 'white-space:nowrap;'},

        ]
        return columns

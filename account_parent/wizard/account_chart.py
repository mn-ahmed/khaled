# -*- coding: utf-8 -*-


from odoo import models, fields, api, _
from odoo.tools.safe_eval import safe_eval
import time
from odoo.exceptions import UserError
from markupsafe import Markup


class OpenAccountChart(models.TransientModel):
	"""
	For Chart of Accounts
	"""
	_name = "account.open.chart"
	_description = "Account Open chart"

	company_id = fields.Many2one('res.company', string='Company', required=True,
								 default=lambda self: self.env.company)
	date_from = fields.Date(string='Start Date')
	date_to = fields.Date(string='End Date')
	target_move = fields.Selection([('posted', 'All Posted Entries'),
									('all', 'All Entries'),
									], string='Target Moves', required=True,
									default='posted')
	display_account = fields.Selection([('all', 'All'), ('movement', 'With movements'),
										# ('not_zero', 'With balance is not equal to 0'),
										], string='Display Accounts', required=True, default='movement',
									   help="`All`: All account will be displayed, `With Movements`: Only accounts that"
											" have a movement based on the conditions given")
	unfold = fields.Boolean('Auto Unfold')
	report_type = fields.Selection([('account', 'Accounts'),
									('account_type', 'Account Type'),
									 ], 'Hierarchy based on', default = 'account',
		help="If you haven't configured parent accounts, then use 'Account Type'")
	show_initial_balance = fields.Boolean(string='Show Initial Balance')


	@api.onchange('date_to')
	def onchange_date_to(self):
		if self.date_from and self.date_to and self.date_to < self.date_from:
			raise UserError(_('End date must be greater than start date!'))
	
	def _build_contexts(self):
		self.ensure_one()
		result = dict()
		result['state'] = self.target_move or ''
		result['display_account'] = self.display_account or 'all'
		result['date_from'] = self.date_from or False
		result['date_to'] = self.date_to or False
		result['report_type'] = self.report_type
		result['strict_range'] = True if result['date_from'] else False
		result['show_parent_account'] = True
		result['company_id'] = self.company_id.id #or self.env.user.company_id.id
		result['active_id'] = self.id
		result['auto_unfold'] = self.unfold
		result['show_initial_balance'] = self.show_initial_balance
		return result
	
	@api.model
	def build_domain_context(self, wiz_id=None, account_id=None):
		domain = []
		context = dict(self.env.context)
		if wiz_id:
			context.update(self.browse(wiz_id)._build_contexts())
		if not context.get('company_id',False):
			return domain, context
		if account_id:
			account = self.env['account.account'].browse(account_id)
			if account.internal_type in ['receivable', 'payable']:
				context.update({'search_default_group_by_partner': True})
			sub_accounts = self.env['account.account'].with_context({'show_parent_account': True}).search([
				('id', 'child_of', [account_id])])
			context.update({'account_ids': sub_accounts})
			tables, where_clause, where_params = self.env['account.move.line'].with_context(context)._query_get()
			query = 'SELECT "account_move_line".id FROM ' + tables + 'WHERE' + where_clause 
			self.env.cr.execute(query, tuple(where_params))
			ids = (x[0] for x in self.env.cr.fetchall())
			list_ids = list(ids)
			domain.append(('id', 'in', list_ids))
		return domain, context

	def account_chart_open_window(self):
		"""
		Opens chart of Accounts
		@return: dictionary of Open account chart window on given date(s) and all Entries or posted entries
		"""
		self.ensure_one()
		result = {
			'name': 'Chart of Account Hierarchy',
			'type': 'ir.actions.client',
			'tag': 'coa_hierarchy',
			'context': """{'url': '/account_parent/output_format/account_parent/active_id',
									'model': 'account.open.chart',
									'active_model': 'account.open.chart'}"""

		}
		if not self.env['account.account'].search([('parent_id','!=',False)], limit=1) and self.report_type == 'account':
			result = self.env.ref('account.action_account_form').read([])[0]
		# else:
			# result = self.env.ref('account.action_account_form').read([])[0]
			# self.report_type = 'account_type'
		used_context = self._build_contexts()
		if 'date_from' in used_context:
			del used_context['date_from']
		if 'date_to' in used_context:
			del used_context['date_to']

		result_context = safe_eval(result.get('context', '{}')) or {}
		used_context.update(result_context)
		result['context'] = str(used_context)
		return result

	@api.model
	def _amount_to_str(self, value, currency):
		""" workaround to apply the float rounding logic of t-esc on data prepared server side """
		return self.env['ir.qweb.field.monetary'].value_to_html(value, {'display_currency': currency})

	@api.model
	def _m2o_to_str(self, value):
		return self.env['ir.qweb.field.many2one'].value_to_html(value, {}) or ''

	@api.model
	def _selection_to_str(self, value, wiz):
		return self.env['ir.qweb.field.selection'].record_to_html(wiz, value, {}) or ''

	@api.model
	def _date_to_str(self, value):
		return self.env['ir.qweb.field.date'].value_to_html(value, {}) or ''

	@api.model
	def _float_html_formating(self, value, company):
		html_formating = True
		if 'output_format' in self._context.keys() and self._context.get('output_format') == 'xls':
			html_formating = False
		return html_formating and self._amount_to_str(value, company.currency_id) or value

	@api.model
	def get_accounts(self, line_id, context):
		return self.env['account.account'].sudo().with_context(context).search([
			('company_id', '=', context.get('company_id', False)), ('parent_id', '=', line_id)])
	
	def line_data(self, level, parent_id, wiz_id=False, account=False):
		return {
			'id': account.id,
			'wiz_id': wiz_id,
			'level': level,
			'unfoldable': account.user_type_id.type == 'view' and True or False,
			'auto_unfold' : self._context.get('auto_unfold',False),
			'model_id': account.id,
			'parent_id': parent_id,
			'code': account.code,
			'name': account.name,
			'ac_type': self._m2o_to_str(account.user_type_id),
			'type': account.user_type_id.type,
			'currency': self._m2o_to_str(account.currency_id),
			'company': self._m2o_to_str(account.company_id),
			'debit': self._float_html_formating(account.debit, account.company_id),
			'credit': self._float_html_formating(account.credit, account.company_id),
			'balance': self._float_html_formating(account.balance, account.company_id),
			'company_obj':account.company_id,
			'show_initial_balance': self._context.get('show_initial_balance',False),
			'initial_balance': self._float_html_formating(account.initial_balance, account.company_id),
			'ending_balance': self._float_html_formating(account.initial_balance + account.balance, account.company_id),
			'db' : account.debit,
			'cr' : account.credit,
			'bal' : account.balance,
			'ini_bal' : account.initial_balance,
			'end_bal' :	account.initial_balance + account.balance
			}

	@api.model
	def _lines(self, wiz_id=None, line_id=None, level=1, obj_ids=[]):
		final_vals = []
		display_account = self._context.get('display_account', 'all')
		for account in obj_ids:
			if display_account == 'movement':
				if account.credit or account.debit:
					final_vals += [self.line_data(level, wiz_id=wiz_id, parent_id=line_id, account=account)]
			else:
				final_vals += [self.line_data(level, wiz_id=wiz_id, parent_id=line_id, account=account)]
			
		return final_vals
	
	@api.model
	def get_account_lines(self, wiz_id=None, line_id=None,level=1):
		accounts = self.get_accounts(line_id, self._context)
		return self._lines(wiz_id, line_id, level=level, obj_ids=accounts)
	
	def account_type_data(self):
		parent_account_types =[
				{'name': _('Balance Sheet'), 'id': -1001, 'parent_id': False,
							'internal_group': ['asset', 'liability', 'equity'], 'atype':False},
				{'name': _('Profit & Loss'), 'id': -1002, 'parent_id': False,
							'internal_group': ['income', 'expense'], 'atype':False},
				{'name': _('Assets'), 'id': -1003, 'parent_id': -1001,
							'internal_group': ['asset'],'atype':False},
				{'name': _('Liabilities'), 'id': -1004, 'parent_id': -1001, 
							'internal_group':['liability'], 'atype':False},
				{'name': _('Equity'), 'id': -1005, 'parent_id': -1001, 
							'internal_group':['equity'], 'atype':False},
				{'name': _('Income'), 'id': -1006, 'parent_id': -1002, 
							'internal_group':['income'], 'atype':False},
				{'name': _('Expense'), 'id': -1007, 'parent_id': -1002, 
							'internal_group':['expense'], 'atype':False},
				]
		parent_account_types_temp = parent_account_types[:]
		for parent_account_type in parent_account_types_temp:
			if not parent_account_type['parent_id']:
				continue
			account_types = self.env['account.account.type'].search([
				('internal_group', 'in', parent_account_type['internal_group'])])
			for account_type in account_types:
				at_data = {
					'name': account_type.name,
					'id': -1 * account_type.id,  # not to mix with account id
					'parent_id': parent_account_type['id'],
					'internal_group': [account_type.internal_group], 'atype':True
				}
				parent_account_types.append(at_data)
		return parent_account_types

	@api.model
	def get_at_accounts(self, at_data, context):
		account_domain = [('company_id', '=', context.get('company_id', False))]
		if not at_data['atype']:
			account_domain += [('user_type_id.internal_group', 'in', at_data['internal_group'])]
		else:
			account_domain += [('user_type_id', '=', at_data['id']*-1)]
		return self.env['account.account'].sudo().with_context(context).search(account_domain)

	def at_line_data(self, at_data, level, wiz_id=False, parent_id=False, accounts=False):
		if not accounts:
			accounts = self.env['account.account'].browse()
		total_credit = sum(accounts.mapped('credit'))
		total_debit = sum(accounts.mapped('debit'))
		total_balance = sum(accounts.mapped('balance'))
		total_initial_balance = sum(accounts.mapped('initial_balance'))
		total_ending_balance = total_initial_balance + total_balance
		company = self.env['res.company'].browse(self._context.get('company_id', False))
		data = at_data.copy()
		data.update({
			'show_initial_balance': self._context.get('show_initial_balance', False),
			'wiz_id': wiz_id,
			'level': level,
			'unfoldable': True,
			'auto_unfold' : self._context.get('auto_unfold', False),
			'model_id': at_data['id'],
			'parent_id': parent_id,
			'code': at_data['name'].upper(),
			'ac_type': 'View',
			'type': 'view',
			'currency': self._m2o_to_str(company.currency_id),
			'company': self._m2o_to_str(company),
			'company_obj': company,
			'debit': self._float_html_formating(total_debit, company),
			'credit': self._float_html_formating(total_credit, company),
			'balance': self._float_html_formating(total_balance, company),
			'initial_balance': self._float_html_formating(total_initial_balance, company),
			'ending_balance': self._float_html_formating(total_ending_balance, company),
			'db': total_debit,
			'cr': total_credit,
			'bal': total_balance,
			'ini_bal': total_initial_balance,
			'end_bal':	total_ending_balance
			})
		return data

	def _at_lines(self, wiz_id, line_id, level=1):
		context = self._context
		final_vals = []
		display_account = context.get('display_account', 'all')
		if not line_id:
			line_id = False
		at_datas = list(filter(lambda x:x['parent_id'] == line_id, self.account_type_data()))
		for at_data in at_datas:
			accounts = self.get_at_accounts(at_data, context)
			if display_account == 'movement':
				if (sum(accounts.mapped('credit')) or sum(accounts.mapped('debit'))):
					final_vals += [self.at_line_data(at_data, level, wiz_id=wiz_id, parent_id=line_id, accounts=accounts)]
			else:
				final_vals += [self.at_line_data(at_data, level, wiz_id=wiz_id, parent_id=line_id, accounts=accounts)]          
		if not at_datas:
			at_datas = list(filter(lambda x:x['id'] == line_id, self.account_type_data()))
			for at_data in at_datas:
				accounts = self.get_at_accounts(at_data, context)
				final_vals += self._lines(wiz_id, line_id, level=level, obj_ids=accounts)
		return final_vals
	
	@api.model
	def get_account_type_lines(self, wiz_id=None, line_id=None, level=1):
		return self._at_lines(wiz_id, line_id, level=level)

	@api.model
	def get_lines(self, wiz_id=None, line_id=None, **kw):
		context = dict(self.env.context)
		if wiz_id:
			self = self.browse(wiz_id)
			context.update(self._build_contexts())
		self = self.with_context(context)
		level = 1
		if kw:
			level = kw.get('level', 0)
		res = []
		if context.get('report_type', 'account_type') == 'account':
			res = self.get_account_lines(wiz_id, line_id, level)
		else:
			res = self.get_account_type_lines(wiz_id, line_id,level)
		reverse_sort = False
		final_vals = sorted(res, key=lambda v: v['code'], reverse=reverse_sort)
		# html_formating = True
# 		if 'output_format' in self._context.keys() and context.get('output_format') == 'xls':
# 			html_formating = False
# 		lines = self.final_vals_to_lines(final_vals, level, html_formating)
		return final_vals


	@api.model
	def get_all_lines(self, line_id=False, level=0):
		self.ensure_one()
		result = []
		for line in self.get_lines(self.id, line_id=line_id, level=level):
			result.append(line)
			if line['type'] == 'view':
				result.extend(self.get_all_lines(line_id=line['model_id'], level=line['level']+1))
		return result
	
	@api.model
	def get_pdf_lines(self):
		lines = self.get_all_lines()
		return lines

	def get_xls_title(self, user_context):
		company = self.env['res.company'].browse(user_context.get('company_id')).name
		date_from = user_context.get('date_from')
		date_to = user_context.get('date_to')
		move = user_context.get('target_move')
		if date_from:
			row_data = [['', '', '', '', '', '', ],
						['Company:', 'Target Moves:', 'Date from:', 'Date to:', ''],
						[company, move, date_from, date_to, ''],
						['', '', '', '', '', '', '', ]]
		else:
			row_data = [['', '', '', '', '', '', ],
						['Company:', 'Target Moves:', ''],
						[company, move, ''],
						['', '', '', '', '', '', '', ]]
		return row_data

	def get_pdf(self, wiz_id):
		report_obj = self.browse(wiz_id)
		user_context = report_obj._build_contexts()
		lines = report_obj.with_context(print_mode=True, **user_context).get_pdf_lines()
		heading = self.get_heading(user_context)
		base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
		rcontext = {
			'mode': 'print',
			'base_url': base_url,
			'company_id': report_obj.company_id,
		}
		user_context.update(rcontext)
		self = self.with_context(user_context)
		user_context.update(report_obj.generate_report_context(user_context))
		body = self.env['ir.ui.view'].with_context(user_context)._render_template(
			"account_parent.report_coa_hierarchy_print",
			values=dict(rcontext, 
						lines=lines,
						heading=heading,
						user_data=user_context,
						# time=time,
						# context_timestamp=lambda t: fields.Datetime.context_timestamp(self.with_context(tz=self.env.user.tz), t),
						report=self, 
						context=self),
		)

		header = self.env['ir.actions.report']._render_template("web.internal_layout", values=rcontext)
		header = self.env['ir.actions.report']._render_template("web.minimal_layout",
																values=dict(rcontext, subst=True,
																			body=Markup(header.decode())))
		return self.env['ir.actions.report']._run_wkhtmltopdf(
			[body],
			header=header.decode(),
			landscape=True,
			specific_paperformat_args={'data-report-margin-top': 10, 'data-report-header-spacing': 10}
		)
	
	def get_heading(self, context):
		res = False
		if context.get('company_id'):
			res = "Chart of Account: %s" % self.env['res.company'].browse(context.get('company_id')).display_name
		return res

	def generate_report_context(self, user_context):
		rcontext = dict()
		rcontext['show_initial_balance'] = user_context.get('show_initial_balance')
		rcontext['date_from'] = self._date_to_str(user_context.get('date_from'))
		rcontext['date_to'] = self._date_to_str(user_context.get('date_to'))
		rcontext['target_move'] = self._selection_to_str('target_move', self)
		rcontext['display_account'] = self._selection_to_str('display_account', self)
		rcontext['report_type'] = self._selection_to_str('report_type', self)
		return rcontext

	def _get_html(self):
		result = {}
		rcontext = {}
		context = self.env.context
		if context.get('active_id') and context.get('active_model') == 'account.open.chart':
			wiz_obj = self.browse(context.get('active_id'))
			user_context = wiz_obj._build_contexts()
			rcontext = wiz_obj.generate_report_context(user_context)
			rcontext['lines'] = self.with_context(user_context).get_lines(wiz_id=user_context.get('active_id'))
			rcontext['heading'] = self.get_heading(user_context)
		result['html'] = self.env.ref('account_parent.report_coa_hierarchy')._render(rcontext)
		return result

	@api.model
	def get_html(self, given_context=None):
		res = self.search([('create_uid', '=', self.env.uid)], order="id desc", limit=1)
		if not res:
			res = self.create({})
		if not given_context:
			given_context = res._build_contexts()
		return res.with_context(given_context)._get_html()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

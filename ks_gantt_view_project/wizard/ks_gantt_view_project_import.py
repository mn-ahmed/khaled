from odoo import models, fields, _
import xlrd
import tempfile
import binascii
import datetime
import logging
import json
import dateutil.parser
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class KsGanttViewImport(models.TransientModel):
    _name = 'ks.gantt.import.wizard'
    _description = 'Ks Project Import Wizard'

    ks_file_type = fields.Selection([('xlsx', 'Excel'), ('json', 'JSON')], string='File Type', default='xlsx',
                                    required=True)
    ks_file = fields.Binary(string='Upload File', required=True)

    def ks_action_import(self):
        if self.ks_file_type == 'xlsx':
            self.ks_import_xlsx_file()
        elif self.ks_file_type == 'json':
            self.ks_import_json_file()

        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    def ks_import_xlsx_file(self):
        # Read xlsx file.
        fp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
        fp.write(binascii.a2b_base64(self.ks_file))
        fp.seek(0)
        try:
            workbook = xlrd.open_workbook(fp.name)
            sheet = workbook.sheet_by_index(0)
        except Exception as e:
            raise ValidationError(_("File can't be read please upload correct file"))

        ks_sheet_columns = []
        ks_project_dict = {}

        ks_project_task_obj = self.env['project.task'].sudo()

        # parsing xlsx data.
        for row_index, row in enumerate(map(sheet.row, range(sheet.nrows)), 1):
            if row_index == 1:
                ks_sheet_columns = row
            else:
                ks_task_write_val = {}
                # read imported data rows and creates a dictionary/
                for index, val in enumerate(ks_sheet_columns):
                    # manage new project creation
                    if val.value == 'project_id':
                        # check if duplicate project not created then created.
                        if row[index].value not in ks_project_dict.keys():
                            # create new project.
                            project_name = row[index].value + " " + str(datetime.datetime.now())
                            new_project_id = self.env['project.project'].sudo().create({
                                'name': project_name
                            })
                            # update project list info
                            ks_project_dict[row[index].value] = new_project_id.id

                        # update dictionary for its project fields
                        ks_task_write_val[val.value] = ks_project_dict[row[index].value]

                    elif ks_project_task_obj._fields[val.value].type in ['char', 'selection']:
                        ks_task_write_val[val.value] = row[index].value
                    elif ks_project_task_obj._fields[val.value].type == 'many2one':
                        ks_task_write_val[val.value] = self.ks_valid_manny_to_one_data(
                            ks_project_task_obj._fields[val.value].comodel_name, row[index].value)
                    elif ks_project_task_obj._fields[val.value].type in ['datetime', 'date']:
                        if row[index].value:
                            ks_task_write_val[val.value] = xlrd.xldate.xldate_as_datetime(row[index].value,
                                                                                          workbook.datemode)
                        else:
                            ks_task_write_val[val.value] = False
                    elif ks_project_task_obj._fields[val.value].type == 'boolean':
                        ks_task_write_val[val.value] = bool(row[index].value)
                    else:
                        _logger.warning(
                            _("%s field type can't imported since it is not supported" % ks_project_task_obj._fields[
                                val.value].type))
                ks_project_task_obj.create(ks_task_write_val)

    def ks_import_json_file(self):
        fp = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
        fp.write(binascii.a2b_base64(self.ks_file))
        fp.seek(0)
        try:
            parsed_data = json.load(fp)
        except Exception as e:
            raise ValidationError(_("File can't be read please upload correct file"))

        if parsed_data['config'] and parsed_data['config']['ks_gantt_task_data'] and \
                parsed_data['config']['ks_gantt_task_data']['data']:
            # create dictionary for project tasks.
            task_data = parsed_data['config']['ks_gantt_task_data']['data']

            # project task object
            ks_project_task_obj = self.env['project.task'].sudo()
            ks_project_dict = {}

            # remove project data from the parsed list.
            filtered_task_data = [rec if rec['type'] != 'project' else None for rec in task_data]
            for task in filtered_task_data:
                ks_task_write_val = {}
                if task:
                    for key, value in self.ks_gantt_field_mapping().items():
                        if value == 'project_id':
                            if task[key] and task[key][1] and task[key][1] not in ks_project_dict.keys():
                                project_name = task[key][1] + " " + str(datetime.datetime.now())
                                new_project_id = self.env['project.project'].sudo().create({
                                    'name': project_name
                                })
                                # update project list info
                                ks_project_dict[task[key][1]] = new_project_id.id
                            # update task dict for new project.
                            ks_task_write_val[value] = ks_project_dict[task[key][1]]

                        elif ks_project_task_obj._fields[value].type in ['char', 'selection']:
                            ks_task_write_val[value] = task.get(key)

                        elif ks_project_task_obj._fields[value].type == 'many2one':
                            # need to check if value is available or not.
                            ks_task_write_val[value] = self.ks_valid_manny_to_one_data(
                                ks_project_task_obj._fields[value].comodel_name, task[key][1]) if task.get(key) and \
                                                                                                  task[key][
                                                                                                      1] else False
                        elif ks_project_task_obj._fields[value].type in ['datetime', 'date']:
                            if task[key]:
                                # ks_task_write_val[value] = dateutil.parser.parse(task[key])
                                ks_task_write_val[value] = fields.Datetime.from_string(
                                    str(dateutil.parser.parse(task[key])).split("+")[0])
                        elif ks_project_task_obj._fields[value].type == 'boolean':
                            ks_task_write_val[value] = bool(task.get(key))
                        else:
                            _logger.warning(
                                _("%s field type can't imported since it is not supported" %
                                  ks_project_task_obj._fields[
                                      value].type))
                    ks_project_task_obj.create(ks_task_write_val)
        else:
            _logger.info(_('Required data not found in the json file, please upload correct json file.'))

    def ks_gantt_field_mapping(self):
        return {
            'text': 'name',
            'mark_as_important': 'priority',
            'project_id': 'project_id',
            'ks_owner_task': 'user_ids',
            'partner_id': 'partner_id',
            # 'company_id': 'company_id',
            'ks_deadline_tooltip': 'date_deadline',
            'unscheduled': 'ks_task_unschedule',
            'type': 'ks_task_type',
            'ks_enable_task_duration': 'ks_enable_task_duration',
            'start_date': 'ks_start_datetime',
            'end_date': 'ks_end_datetime',
            'ks_schedule_mode': 'ks_schedule_mode',
            'constraint_type': 'ks_constraint_task_type',
            'constraint_date': 'ks_constraint_task_date',
            'stage_id': 'stage_id',
        }

    def ks_valid_manny_to_one_data(self, comodel, value):
        """
        Function to check if data is available then return its id otherwise return false.
        :param comodel:
        :param id:
        :return:
        """
        ks_domain = []
        # Create domain to search the records.
        if self.env[comodel].sudo()._fields['name']:
            ks_domain.append(('name', '=', value))
        else:
            ks_domain.append(('display_name', '=', value))

        ks_res = self.env[comodel].sudo().search(ks_domain, limit=1)
        if ks_res:
            return ks_res.id
        else:
            return False

odoo.define('account_parent.CoAWidget', function (require) {
'use strict';

var core = require('web.core');
var Widget = require('web.Widget');
var pyUtils = require('web.py_utils');

var QWeb = core.qweb;

var _t = core._t;

var CoAWidget = Widget.extend({
    events: {
        'click span.o_coa_foldable': 'fold',
        'click span.o_coa_unfoldable': 'unfold',
        'click td.o_coa_action': 'boundLink',
    },
    init: function(parent) {
        this._super.apply(this, arguments);
    },
    start: function() {
        QWeb.add_template("/account_parent/static/src/xml/account_parent_line.xml");
        return this._super.apply(this, arguments);
    },
    boundLink: function(e) {
        e.preventDefault();
        var self = this
        var account_id = $(e.currentTarget).data('id');
        var account_name = $(e.currentTarget).data('name');
        var wiz_id = $(e.currentTarget).data('wiz_id');
        return self._rpc({
            model: 'account.open.chart',
            method: 'build_domain_context',
            args: [parseInt(wiz_id, 10), parseInt(account_id, 10)],
        })
            .then(function (result) {
//            	if (!result[1].hasOwnProperty('company_id')) {
//                    self.displayNotification({message: _t("Journal items is not available for current report"),type:'danger' });
//                    return;
//                }
//                else {
                var results = pyUtils.eval_domains_and_contexts({
                    domains: [result[0]],
                    contexts: [result[1]],
                    group_by_seq: [],
                });
                
                return self.do_action({
                    name: 'Journal Items ('+ account_name + ')',
                    type: 'ir.actions.act_window',
                    res_model: 'account.move.line',
                    domain: results.domain,
                    context: results.context,
                    views: [[false, 'list'], [false, 'form']],
                    view_type: "list",
                    view_mode: "form",
                    target: 'current'
                });
//                }
            });
        
    },
    removeLine: function(element) {
        var self = this;
        var el, $el;
        var rec_id = element.data('id');
        var $coaEl = element.nextAll('tr[data-parent_id=' + rec_id + ']')
        for (el in $coaEl) {
            $el = $($coaEl[el]).find(".o_coa_domain_line_0, .o_coa_domain_line_1");
            if ($el.length === 0) {
                break;
            }
            else {
                var $nextEls = $($el[0]).parents("tr");
                self.removeLine($nextEls);
                $nextEls.remove();
            }
            $el.remove();
        }
        return true;
    },
    fold: function(e) {
        this.removeLine($(e.target).parents('tr'));
        var active_id = $(e.target).parents('tr').find('td.treeview-td').data('id');
//        $(e.target).parents('tr').find('td.o_coa_foldable').attr('class', 'o_coa_unfoldable ' + active_id); // Change the class, rendering, and remove line from model
        $(e.target).parents('tr').find('span.o_coa_foldable').replaceWith(QWeb.render("coa_unfoldable", {lineId: active_id}));
        $(e.target).parents('tr').toggleClass('o_coa_unfolded');
    },
    autounfold: function(target) {
    	var self = this;
        var $CurrentElement;
        $CurrentElement = $(target).parents('tr').find('td.treeview-td');
        var active_id = $CurrentElement.data('id');
        var wiz_id = $CurrentElement.data('wiz_id');
        var active_model_id = $CurrentElement.data('model_id');
        var row_level = $CurrentElement.data('level');
        var $cursor = $(target).parents('tr');
        this._rpc({
                model: 'account.open.chart',
                method: 'get_lines',
                args: [parseInt(wiz_id, 10), parseInt(active_id, 10)],
                kwargs: {
                    'model_id': active_model_id,
                    'level': parseInt(row_level) + 1 || 1
                },
            })
            .then(function (lines) {// After loading the line
            	_.each(lines, function (line) { // Render each line
                    $cursor.after(QWeb.render("report_coa_lines", {l: line}));
                    $cursor = $cursor.next();
                    if (line["auto_unfold"]) {
                       if ($cursor && line.unfoldable) {
                           self.autounfold($cursor.find(".fa-caret-right"));
                       }
                    }
            	});

                
            });
//        $CurrentElement.attr('class', 'o_coa_foldable ' + active_id); // Change the class, and rendering of the unfolded line
        $(target).parents('tr').find('span.o_coa_unfoldable').replaceWith(QWeb.render("coa_foldable", {lineId: active_id}));
        $(target).parents('tr').toggleClass('o_coa_unfolded');
    },
    unfold: function(e) {
        this.autounfold($(e.target));
    },

});

return CoAWidget;

});

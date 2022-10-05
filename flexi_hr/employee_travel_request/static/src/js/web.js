odoo.define('aspl_hr_travel.main', function (require) {
"use strict";

   var FormRenderer = require('web.FormRenderer');
   var rpc = require('web.rpc');
   var session = require('web.session');

   FormRenderer.include({
        _renderHeaderButtons: function (node) {
            var self = this;
            var $buttons = $('<div>', {class: 'o_statusbar_buttons'});
            _.each(node.children, function (child) {
                if (child.tag == 'button') {
                    if ((self.state.model == 'hr.emp.travel.request' && child.attrs.name == 'action_confirm') || (self.state.model == 'hr.emp.travel.request' && child.attrs.name == 'action_reject')){
                        if (self.state.context.uid == self.state.data.user_id.res_id){
                            $buttons.append(self._renderHeaderButton(child));
                        }
                        else{
                            var flag = false;
                            _.each(self.state.data.hr_manager_user_ids.data, function(record){
                                if (self.state.context.uid == record.data.id){
                                    flag=true;
                                }
                            })
                            if(flag){
                                $buttons.append(self._renderHeaderButton(child));
                            }
                        }
                    }else{
                        $buttons.append(self._renderHeaderButton(child));
                    }
                }
            });
            return $buttons;
        },
   });
});
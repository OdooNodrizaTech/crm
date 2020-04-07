odoo.define('crm_activity_objective.tree_view_button', function (require){
"use strict";
    var ListView = require('web.ListView');
    var Model = require('web.DataModel');
    var Dialog = require('web.Dialog');
    
    ListView.include({
        render_buttons: function() {
            this._super.apply(this, arguments)
            if (this.$buttons) {
                this.$buttons.find('.o_crm_lead_pedir_dormido_button').on('click', this.proxy('crm_lead_pedir_dormido_button'));                
                this.$buttons.find('.o_crm_lead_pedir_activo_button').on('click', this.proxy('crm_lead_pedir_activo_button'));
            }
        },
        crm_lead_pedir_dormido_button: function() {
            new Model('crm.lead')
                .call('action_boton_pedir_dormido', [[]])
                .then(function(result) {
                    if(result.errors==true)
                    {
                        Dialog.confirm(self, result.error, {
                            title: 'Error',
                        });                                                                        
                    }
                    else
                    {
                        location.reload();
                    }
                })
        },
        crm_lead_pedir_activo_button: function() {
            new Model('crm.lead')
                .call('action_boton_pedir_activo', [[]])
                .then(function(result) {                    
                    if(result.errors==true)
                    {
                        Dialog.confirm(self, result.error, {
                            title: 'Error',
                        });
                    }
                    else
                    {
                        location.reload();
                    }
                })
        }
    });
});
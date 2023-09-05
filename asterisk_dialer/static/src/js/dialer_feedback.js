odoo.define("asterisk_dialer.inherit_base_dialer_button", function (require) {
    "use strict";

const DialingPanel = require('voip.DialingPanel');
const Widget = require('web.Widget');
var core = require('web.core');
var session = require('web.session');

    // overwrite the base dialer function 

    DialingPanel.include({
      _onClickHangupButton(ev){
        this._userAgent.hangup();
        this._cancelCall();
        this._activeTab._selectPhoneCall(this._activeTab._currentPhoneCallId);
        const details = document.getElementsByClassName('o_dial_call_number');

        // for(var i=0; i<=details.length; i++)
        // {
        //     var data = details[i];
        //     console.log(data,'vvvvvvvvvvvvvvvv');
        // };
        
        // get the current window url
        var current_url = window.location.href; 
        if ((current_url.split(/id=(.*)/)[1])) {
            // get the values after id from the url 20-09-22
            var cr_id = (current_url.split(/id=(.*)/)[1])
            // get the values after the model from the url 20-09-22         
            var cr_model = (current_url.split(/model=(.*)/)[1]) 
            // using split to get the values from model and id  
            var current_model_ids = cr_id.split("&");
            var current_model = cr_model.split("&");
            // while click the call end button to open the feedback wizard using below code 16-09-22
            this.do_action({
                name:"outbound",
                res_model: "call.feedback",
                target: 'new',
                type: 'ir.actions.act_window',
                views: [[false, 'form']],
                context:{'default_current_model':current_model[0],'default_current_id':current_model_ids[0]},
                });
        }
      },
    });
  });

       
       
            

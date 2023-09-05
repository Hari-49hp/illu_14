// odoo.define(ppts_custom_apt_mgmt.EditableListRenderer, function (require) {
//   "use strict";

//   var ListRenderer = require('web.ListRenderer');

//   ListRenderer.include({
//     _renderHeaderCell: function (node) {
//       const $th = this._super.apply(this, arguments);
//       if (node.attrs.class === 'custom_identifier'){
//         $th.text(node.attrs.string);
//       }
//       return $th;
//     },
//   });

// });
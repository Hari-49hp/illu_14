odoo.define("custom_pos.models", function(require) {
	"use strict";
	
	var models = require('point_of_sale.models');
	var DB = require('point_of_sale.DB');
	var utils = require('web.utils');
	var session = require('web.session');
	var rpc = require('web.rpc');
	localStorage.setItem("search_product_ids",[]);
	
	
	models.load_fields("product.product", ['type'])
	
	models.PosModel.prototype.models.push({
        model: 'ir.model.fields',
        fields: ['name','field_description'],
        domain: [['model_id.model', '=', 'product.product'],['name','in',['name','default_code','barcode','description','description_sale']]],
        loaded: function(self, product_fields){
            self.db.add_product_fields(product_fields);
        },
    });
	
	DB.include({
	
        init: function(options){
            this._super.apply(this, arguments);
            this.product_fields = [];
            this.product_type = "type=product";
            this.limit = 1000;
        },
        add_product_fields: function(product_fields){
        	for(var i = 0, len = product_fields.length; i < len; i++){
        		var product_field = product_fields[i];
            	this.product_fields.push(product_field);
            }
        },
        
        /*
        _product_search_string: function(product){
	        var str = product.display_name;
	        if (product.barcode) {
	            str += '|' + product.barcode;
	        }
	        if (product.default_code) {
	            str += '|' + product.default_code;
	        }
	        if (product.description) {
	            str += '|' + product.description;
	        }
	        if (product.description_sale) {
	            str += '|' + product.description_sale;
	        }
	        if (product.type) {
            	str += '|type=' + product.type;
        	}
	        str  = product.id + ':' + str.replace(/:/g,'') + '\n';
	        return str;
    	},
    	*/
    	 /* returns a list of products with :
	     * - a category that is or is a child of category_id,
	     * - a name, package or barcode containing the query (case insensitive) 
	     */
	    search_product_in_category: function(category_id, query){
	   		
	        /* 
	        var type_results_ids = [];
	        var re1 = RegExp("([0-9]+):.*?"+utils.unaccent(this.product_type),"gi");
	        for(var i = 0; i < this.limit; i++){
            	var r1 = re1.exec(this.category_search_string[category_id]);
            
	            if(r1){
	            		var id = Number(r1[1]);
	                	type_results_ids.push(id);
	            }else{
	                break;
	            }
        	}
        	*/
        	
           var domain = []
           var type = ''
           
           if (this.product_type == "type=product") {
           		type = 'product';
           } else {
           		type = 'service';
           }
           
           if ($(".custom-field-search").val() == 'all_fields') {
           		domain = ['|','|','|','|',['name','ilike',query],['default_code','ilike',query],['barcode','ilike',query],['description','ilike',query],['description_sale','ilike',query],['type','=',type]]
           } else {
           		domain = [[$(".custom-field-search").val(),'ilike',query],['type','=',type]]
           }
           
           var search_product_ids = rpc.query({
	            model: 'product.product',
	            method: 'search_read',
	            fields: ['id'],
	            domain: domain,
	        }).then(function (ids) {
	            var pro_ids = [];
	            _.each(ids, function(id) {
	                pro_ids.push(id.id);
	            });
	             localStorage.setItem("search_product_ids", pro_ids);
	        })
                
            
            try {
	            query = query.replace(/[\[\]\(\)\+\*\?\.\-\!\&\^\$\|\~\_\{\}\:\,\\\/]/g,'.');
	            query = query.replace(/ /g,'.+');
	            var re = RegExp("([0-9]+):.*?"+utils.unaccent(query),"gi");
	        }catch(e){
	            return [];
	        }
	        
	        var results = [];
	        for(var i = 0; i < this.limit; i++){
	            var r = re.exec(this.category_search_string[category_id]);
	           if(r && localStorage.getItem("search_product_ids")){
	                var id = Number(r[1]);
	                if(localStorage.getItem("search_product_ids").indexOf(id) !== -1){
					        results.push(this.get_product_by_id(id));
					    }
	            }else{
	                break;
	            }
	        }
	        return results;
	    },
	    
	    get_product_by_category: function(category_id){
	        var product_ids  = this.product_by_category_id[category_id];
	        var list = [];
	        if (product_ids) {
	            for (var i = 0, len = Math.min(product_ids.length, this.limit); i < len; i++) {
	            	if ('type='+this.product_by_id[product_ids[i]].type == this.product_type) {
	                	list.push(this.product_by_id[product_ids[i]]);
	                }
	            }
	        }
	        return list;
    	},
    	
        
        
    });
    



});
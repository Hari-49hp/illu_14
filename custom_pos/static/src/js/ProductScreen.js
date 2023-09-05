odoo.define('custom_pos.ProductScreen', function (require) {
    'use strict';

    const ProductScreen = require('point_of_sale.ProductsWidget');
    const Registries = require('point_of_sale.Registries');

	
    const custom_posProductScreen = (ProductScreen) =>
        class extends ProductScreen {
            constructor() {
                super(...arguments);
            }
            
	        get productsToDisplay() {
	        
	        	if ($('.custom-category-search').val() == -1) {
	        		return [];
	        	}
	        
	            if (this.searchWord !== '') {
	                return this.env.pos.db.search_product_in_category(
	                    this.selectedCategoryId,
	                    this.searchWord
	                );
	            } else {
	                return this.env.pos.db.get_product_by_category(this.selectedCategoryId);
	            }
	        }
            
	        get subcategories() {
	        
	        	let all_categories = [];
	        	
				Object.keys(this.env.pos.db.category_childs).forEach((key) => {
				   this.env.pos.db.category_childs[key].map(id => this.env.pos.db.get_category_by_id(id)).forEach(function(child){
	               		all_categories.push(child)
	                });
				  
				});
		        
		        return all_categories;
		        
	        }
	        
	        _switchCategory(event) {
	        	this.env.pos.set('selectedCategoryId', -1);
	            this.env.pos.set('selectedCategoryId', event.currentTarget.value);
	        }
	        
	        _switchFieldSearch() {
	        	var selectedCategoryId = this.env.pos.get('selectedCategoryId')
	            this.env.pos.set('selectedCategoryId', 0);
	            this.env.pos.set('selectedCategoryId', selectedCategoryId);
	        }
	        
	        updateSearch(event) {
	        
	            this.env.pos.set('selectedCategoryId', event.currentTarget.value);
	        }
	       	
	       	get_type_search_product() {
	            this.env.pos.db.product_type = 'type=product';
	            this.env.pos.set('selectedCategoryId', 1);
	            this.env.pos.set('selectedCategoryId', 0);
	            $(".custom-category-search").val(0);
	            $("#nav-products-tab").addClass('active');
	            $("#nav-service-tab").removeClass('active');
	            
	        }
	        
	        get_type_search_service() {
	            this.env.pos.db.product_type = 'type=service';
	            this.env.pos.set('selectedCategoryId', 1);
	            this.env.pos.set('selectedCategoryId', 0);
	            $(".custom-category-search").val(0);
	            $("#nav-products-tab").removeClass('active');
	            $("#nav-service-tab").addClass('active');
	        }
	        
            
        };

    Registries.Component.extend(ProductScreen, custom_posProductScreen);

    return ProductScreen;
});

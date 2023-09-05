odoo.define('point_of_sale.ProductsWidgetControlPanel_custom', function(require) {
    'use strict';

    const { useRef } = owl.hooks;
    const { debounce } = owl.utils;
    const ProductsWidgetControlPanel = require('point_of_sale.ProductsWidgetControlPanel');
    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');

    class ProductsWidgetControlPanel_custom extends PosComponent {
        constructor() {
            super(...arguments);
            this.updateSearch = debounce(this.updateSearch, 100);
        }
        
        updateSearch(event) {
            this.trigger('update-search', event.target.value);
            /* if (event.key === 'Enter') {
                // We are passing the searchWordInput ref so that when necessary,
                // it can be modified by the parent.
                alert(event.target.value);
                this.trigger('try-add-product', { searchWordInput: event });
            }*/
        }
    }
    
    ProductsWidgetControlPanel_custom.template = 'ProductsWidgetControlPanel_custom';

    Registries.Component.add(ProductsWidgetControlPanel_custom);

    //return ;
    
   
   const ProductsWidgetControlPanel02 = (ProductsWidgetControlPanel) =>
    
     class extends ProductsWidgetControlPanel {
        constructor() {
            super(...arguments);
        }
        
    	get_type_search_product() {
            this.env.pos.db.product_type = 'type=product';
            this.env.pos.set('selectedCategoryId', 0);
            this.env.pos.set('selectedCategoryId', -1);
            $(".custom-category-search").val(-1);
            $("#nav-products-tab").addClass('active');
            $("#nav-service-tab").removeClass('active');
        }
        
        get_type_search_service() {
            this.env.pos.db.product_type = 'type=service';
            this.env.pos.set('selectedCategoryId', 0);
            this.env.pos.set('selectedCategoryId', -1);
            $(".custom-category-search").val(-1);
            $("#nav-products-tab").removeClass('active');
            $("#nav-service-tab").addClass('active');
        }
    }
    

   Registries.Component.extend(ProductsWidgetControlPanel, ProductsWidgetControlPanel02);

    return ProductsWidgetControlPanel02, ProductsWidgetControlPanel_custom;
    


});

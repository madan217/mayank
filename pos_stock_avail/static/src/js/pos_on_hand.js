 odoo.define('pos_product_restrict', function (require) {

"use strict";

var models = require('point_of_sale.models');
var restrict_popup = require('point_of_sale.popups');
var _t  = require('web.core')._t;
var gui = require('point_of_sale.gui');
var _super_order = models.Order.prototype;

var RestrictQtyPopupWidget = restrict_popup.extend({
    template: 'RestrictQtyPopupWidget',
    show: function(options){
        this._super(options);
        this.focus();
    },

    click_confirm: function(){
        this.gui.close_popup();
    },

    focus: function(){
        this.$("input[autofocus]").focus();
        this.focus_model = false;   // after focus clear focus_model on widget
    }
});
gui.define_popup({name:'restrictzeroqty', widget:RestrictQtyPopupWidget});

models.Order = models.Order.extend({

	display_qty_restrict_popup: function() {
            this.pos.gui.show_popup('restrictzeroqty', {
                'title': _t('You have not available stock'),
            });
    },

	add_product: function (product, options) {
            
            if (product.qty_available <= 0) {
                return this.display_qty_restrict_popup();
            }
            var data = _super_order.add_product.apply(this, arguments);
            return data
        },
    });
});



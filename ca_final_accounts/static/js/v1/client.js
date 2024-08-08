jQuery(function(){
    jQuery("body").on("submit", ".cls_frm_login", function(e){
        /* login api */
        e.preventDefault();
        let _obj = {};
        $app.debug(_obj);
        let login_form = $(e.target);
        _obj.SRC = "/api/v1/login/";
        _obj.DATA = ConvertFormToJSON(login_form);
        $app.io.makeRequest(_obj, function(r){
            $app.sec = r;
            set_s_key("access", r.access);
            set_s_key("refresh", r.refresh);
            // enable session login.
            (function(){
                let _obj1 = {};
                _obj1.SRC = "/api/v1/login/session/";
                $app.io.makeRequest(_obj1, function(r){
                    top.window.location = '/my-app/';
                });
            })();
            // every 24M token refresh.
            // setInterval(fun_refresh_token, 24*60*1000);
        });
    });

    // add question add row
    jQuery("body").on("click", "button.addthis", function(e){
        let _tbody = jQuery('#myTable tbody');
        let _table = _tbody.length ? _tbody : jQuery('#myTable');
        let _row = '<tr>'+
            '<td>{{dr_balance}}</td>'+
            '<td>{{dr_amount}}</td>'+
            '<td>{{cr_balance}}</td>'+
            '<td>{{cr_amount}}</td>'+
        '</tr>';
        //Add row
        _sel_attr = "sel_attr_"+jQuery('#myTable tbody tr').length;
        _table.append(_row.compose({
            'dr_balance': '<select class="select-one sel_attr '+_sel_attr+'" name="dr_attr_code" required="required" ><option value="">-- Please choose an option --</option></select>',
            'dr_amount': '<input type="number" name="dr_amount" min="0" class="inp-num">',
            'cr_balance': '<select class="select-one sel_attr '+_sel_attr+'" required="required" name="cr_attr_code"><option value="">--Please choose an option --</option></select>',
            'cr_amount': '<input type="number" name="cr_amount" min="0" class="inp-num">'
        }));
        populate_attributes("select."+_sel_attr);
    });

    jQuery("body").on("submit", ".cls_add_question", function(e){
        /* login api */
        e.preventDefault();
        let _obj = {};
        let login_form = $(e.target);
        $app.debug(_obj);
        _obj.SRC = "/api/v1/question/add/";
        _obj.METHOD = "POST";
        _obj.DATA = {
            title:"Question",
            dr_attr_code:[],
            dr_amount:[],
            cr_attr_code: [],
            cr_amount: [],
            adj_attr_code: [],
            adj_amount:[]
        };
        _obj.f_s_a = login_form.serializeArray();
        _obj._name = void 0;
        jQuery.each(_obj.f_s_a, function(i, itm){
            _obj._name = itm.name;
            if (itm.name == "title"){
                _obj.DATA.title = itm.value;
            }else{
                _obj.DATA[_obj._name].push(itm.value);
            }
        });

        $app.io.makeRequest(_obj, function(r){
            // enable session login.
        });
    });

    // start slider
//    $('.example-1').square1({caption: 'none',
//        theme: 'light'});
    // end slider

    // start navigation
    $(".nav-toggle").click(function () {
      $(".nav-menu").slideToggle();
    });

    $(window).resize(function () {
      if ($(window).width() > 768) {
        $(".nav-menu").removeAttr("style");
      }
    });

    $("ul li").hover(function () {
      $(this).
      children("ul").
      stop().
      slideToggle(500);
    });
    // end navigation


});

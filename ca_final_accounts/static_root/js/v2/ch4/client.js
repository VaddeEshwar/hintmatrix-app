//$app.data_store.dynamic_template = "";

const discount_select = (tbl, tbl_code, _slug, _qun_slug, _amount, position) => {
    let options = [
        {"lbl": "#account# ...DR", "dr-cr": "dr"},
        {"lbl": "To #account#", "dr-cr": "cr"}];

    let _sel_opt = "<select class='cls_move_particular'><option value=''>-:Journal Entry:-</option>";
    /*
    <div class="plus-but cls_move_particular" data-act="tr#dr#add"
    data-qun-slug="1f0c2a44-2b45-44ed-8918-351d3df0eccf"
    data-slug="d2cda2f1-7ff2-4bb5-89ea-4a8727d2f117">add</div>
    */
    _html2 = "";
     options.forEach(function(itm, idx){
        _html2 = $app.data_store._html_first_table_option.replace(/#qun-slug#/g, _qun_slug);
        _html2 = _html2.replace(/#slug#/g, _slug);
        _html2 = _html2.replace(/#label#/g, itm.lbl.replace(/#account#/, tbl));
        _html2 = _html2.replace(/#code#/g, tbl_code+"#"+itm["dr-cr"]+"#add");
        _html2 = _html2.replace(/#step#/g, tbl_code+"#"+itm["dr-cr"]+"#add");

        if(position > 1){
            _html2 = _html2.replace(/#amount#/g, _amount);
            _html2 = _html2.replace(/#position#/g, 2);
        }else{
            _html2 = _html2.replace(/#amount#/g, _amount);
            _html2 = _html2.replace(/#position#/g, 1);
        }
        _sel_opt += _html2;
     });

     return _sel_opt + "</select>";
};

jQuery(function(){

     if(jQuery("#id_html_ans_box").length > 0){
        $app.data_store["_html_first_table_option"] = ('<option data-amount="#amount#" '
        +'data-amount-position="#position#" data-qun-slug="#qun-slug#" data-slug="#slug#" '
        +'data-act="#step#" value="#code#">#label#</option>');
        let id_html_qun_tbl = jQuery("#id_html_qun_tbl").html();
        $app.data_store["id_html_qun_tbl"] = id_html_qun_tbl.trim();
        jQuery("#id_html_qun_tbl").remove();
        let id_html_ans_box = jQuery("#id_html_ans_box").html();
        $app.data_store["id_html_ans_box"] = id_html_ans_box.trim();
        jQuery("#id_html_ans_box").remove();
    }

    jQuery("body").on("change", ".cls_sel_tbl_step1", function(e){
        $app.debug(e);
        let _jObj = $(e.target.selectedOptions);
        _jObj.XHR = {};
        _jObj.XHR.code = _jObj.attr("value");
        _jObj.XHR.action = _jObj.attr("data-act")+"#"+_jObj.XHR.code;
        _jObj.XHR.slug = _jObj.attr("data-slug");
        _jObj.XHR.qun_slug = _jObj.attr("data-qun-slug");
        _jObj.XHR.amount = _jObj.attr("data-amount");
        _jObj.XHR.position = _jObj.attr("data-amount-position");
        $app.debug(_jObj.XHR);
        _jObj.XHR.csrfmiddlewaretoken = jQuery("[name=csrfmiddlewaretoken]").val();
        const url = top.location.pathname+"step1/";
        jQuery.post(url, _jObj.XHR, function(res){
            switch(res.status){
                case "FAILURE":
                    $app.debug(res);
                    let _help = res["data"][0]["help"][0];
                    _help = _help.replace(/<br\/>/g, "\n");
                    let txt = "Wrong!!!<br/> <a href='javascript:void(0)'><abbr title='"+_help+"'>help</abbr></a>";
//                    $(e.target).parent().next().text(res["data"][0]["error"][0]);
                    $(e.target).parent().next().html(txt);
                    let history = JSON.parse(res["data"][0]["history"][0]);
                    $(e.target).parent().next().next().empty().text("-");
                break;
                case "SUCCESS":
                    $(e.target).parent().next().text("-");
                    let account = $(e.target.selectedOptions).text();
                    let sel = discount_select(account, _jObj.XHR.code, _jObj.XHR.slug, _jObj.XHR.qun_slug, _jObj.XHR.amount, _jObj.XHR.position);
                    $(e.target).parent().next().next().empty().html(sel);
                break;
            }
        });

        /*
        1. get option value with slug
        2. sent to BE, for verification of any one table.
        3. if false, hint matrix for the same
        4. else enable second selection box.
        */
    });

    jQuery("body").on("mouseover", ".cls_show_ans_box", function(e){
        e.preventDefault();
        let _this = jQuery(this);
        let _slug = _this.attr("data-slug");
        let _attr = _this.attr("data-attr");
        let _qun_slug = _this.attr("data-qun-slug");
        let _amount = _this.attr("data-amount");
        let _amount2 = _this.attr("data-amount2");
        let _particular = _this.attr("data-particular");
        let _position = _this.attr("data-amount-position");

        let _parent = _this.parent();
        _parent.find(".tooltiptext").remove();

        let _jObj = jQuery(this);
        _jObj.XHR = {};
        _jObj.XHR.slug = _jObj.attr("data-slug");
        _jObj.XHR.csrfmiddlewaretoken = jQuery("[name=csrfmiddlewaretoken]").val();
        let url = "/my-app/question/ch4/table/";
        jQuery.post(url, _jObj.XHR, function(res){
            switch(res.status){
                case "FAILURE":
                break;
                case "SUCCESS":
                    _data = res.data;
                    _s_data = res.s_data;
                    upon = _s_data.upon || "tbl2";
                    _sel_opt = "<option>-:Account Name:-</option>";
                    _upon_tbl = (upon === "tbl3")? 3 : 2;

                    _html2 = "";
                     _data.forEach(function(itm, idx){
                        _html2 = $app.data_store._html_first_table_option.replace(/#qun-slug#/g, _qun_slug);
                        _html2 = _html2.replace(/#slug#/g, _slug);
                        _html2 = _html2.replace(/#label#/g, itm.name);
                        _html2 = _html2.replace(/#step#/g, "step1");
                        _html2 = _html2.replace(/#code#/g, itm.code);

                        if(itm.amount > 1){
                            _html2 = _html2.replace(/#amount#/g, _amount2);
                            _html2 = _html2.replace(/#position#/g, 2);
                        }else{
                            _html2 = _html2.replace(/#amount#/g, _amount);
                            _html2 = _html2.replace(/#position#/g, 1);
                        }
                        _sel_opt += _html2;
                     });

                    _in_html = "";
                    for(let i=0; i<_upon_tbl; i++){
                         _html1 = $app.data_store.id_html_qun_tbl.replace(/#index#/g, (i+1));
                         _html1 = _html1.replace(/#selectName#/g, (i+1));
                         _html1 = _html1.replace(/#selClass#/g, "cls_sel_tbl_step1");
                         _html1 = _html1.replace(/#selectOption#/g, _sel_opt);

                         _in_html += _html1;
                    }

//                    console.log(_in_html);

//                    _data.forEach(function(itm, idx){
//                        _html1 = $app.data_store.id_html_qun_tbl.replace(/#table#/g, itm.name);
//                        _html1 = _html1.replace(/#index#/g, (idx+1));
//                        _html1 = _html1.replace(/#selectName#/g, itm.code);
//
//                        _html1 = _html1.replace(/#code#/g, itm.code);
//                        _html1 = _html1.replace(/#qun-slug#/g, _qun_slug);
//                        _html1 = _html1.replace(/#slug#/g, _slug);
//                        if(itm.amount > 1){
//                            _html1 = _html1.replace(/#amount#/g, _amount2);
//                            _html1 = _html1.replace(/#position#/g, 2);
//                        }else{
//                            _html1 = _html1.replace(/#amount#/g, _amount);
//                            _html1 = _html1.replace(/#position#/g, 1);
//                        }
//                    });

                    let _html = $app.data_store.id_html_ans_box.replace(/#particular#/, _particular);
                    _html = _html.replace(/#attribute#/g, _attr);
                    _html = _html.replace(/#tables#/g, _in_html);

                    if(checkInteger(_amount2) == true && parseFloat(_amount2) != 0){
                        _html = _html.replace(/#amount#/g, _amount+"/"+_amount2);
                    }else{
                        _html = _html.replace(/#amount#/g, _amount);
                    }
                    _parent.append(_html);
                break;
            }
        });
    });
});

function answer_success_cb(data, _jObj, slug, position){
    if(_jObj[0].tagName == "OPTION"){
        _jObj = _jObj.parent();
    }
    _jObj.parent().next().empty().append("correct");
    _data = data;
    action = _data.action;
    amount = _data.amount;
    slug = _data.slug;
    particular_name = jQuery('[data-slug="'+slug+'"].cls_lbl').text();

    add_answered_row(slug, action, particular_name, amount, data.order, data.pair, data.tbl_name, position);

    _history = _data.history;
    if(_history){
        _history = JSON.parse(_history)
        _history.forEach(function(itm, idx){
            add_history_row(-1, itm.description, itm.valid, itm.action);
        });
    }
}

function add_answered_row(slug, action_array, particular_name, amount, order_by, pair, table_name, position){
    let row_from_ac = '<tr class="#slug# first"><td>#transaction#</td><td class="narration-1st">#from-a/c#</td>';
    row_from_ac += '<td>&nbsp;</td><td class="#slug# dr">#amount-dr#</td><td class="#slug# cr">#amount-cr#</td></tr>';
    row_from_ac += '#row-to-a/c#';
    row_from_ac += '<tr class="#slug# last"><td>&nbsp;</td><td class="narration-bottom-border">';
    row_from_ac += '(Being #b_transaction#)</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td></tr>';

    let row_to_ac = '<tr class="#slug# middle"><td>&nbsp;</td>';
    row_to_ac += '<td class="narration-tab-8">#to-a/c#</td>';
    row_to_ac += '<td>&nbsp;</td><td class="#slug# dr">#amount-dr#</td><td class="#slug# cr">';
    row_to_ac += '#amount-cr#</td></tr>';

    let tbody = jQuery("#jr-1 tbody");

    let row_middle = row_to_ac.replace(/#slug#/g, slug);

    action_array.forEach(function(itm, idx){
        // itm = tbl_code#header_code#operation
        itm = itm.split("#");

        if(jQuery("."+slug+".first").length < 1){
            // first time
            let r_f = row_from_ac.replace(/#slug#/g, slug);
            r_f = r_f.replace(/#transaction#/g, particular_name);
            let name = particular_name;
            if(itm[1] == 'cr'){
                row_middle = row_middle.replace(/#to-a\/c#/, make_cr_narration(table_name));
                row_middle = row_middle.replace(/#amount-cr#/g, amount);
                row_middle = row_middle.replace(/#amount-dr#/g, "");

                r_f = r_f.replace(/#amount-cr#/g, "&nbsp;");
                r_f = r_f.replace(/#amount-dr#/g, "");
                r_f = r_f.replace(/#from-a\/c#/g, "");
            }else{
                r_f = r_f.replace(/#from-a\/c#/g, make_dr_narration(table_name));
                r_f = r_f.replace(/#amount-dr#/g, amount);
                r_f = r_f.replace(/#amount-cr#/g, "&nbsp;");

                row_middle = row_middle.replace(/#amount-cr#/g, "");
                row_middle = row_middle.replace(/#amount-dr#/g, amount);
                row_middle = "";
            }
            r_f = r_f.replace(/#b_transaction#/g, particular_name);
            r_f = r_f.replace(/#row-to-a\/c#/, row_middle);

            jQuery("#jr-1 tbody").append(r_f);
        }else{
            // second time
            if(itm[1] == 'cr'){
                row_middle = row_middle.replace(/#to-a\/c#/, make_cr_narration(table_name));
                row_middle = row_middle.replace(/#amount-cr#/g, amount);
                row_middle = row_middle.replace(/#amount-dr#/g, "");
                jQuery( row_middle ).insertBefore( jQuery("."+slug+".last") );
            }else{
                if(jQuery("."+slug+".first td.narration-1st").text().trim() == ""){
                    jQuery("."+slug+".first td.narration-1st").text(make_dr_narration(table_name));
                    jQuery("."+slug+".first td.dr").text(amount);
                }else{
                    row_middle = row_middle.replace(/#to-a\/c#/, make_dr_narration(table_name));
                    row_middle = row_middle.replace(/#amount-cr#/g, "");
                    row_middle = row_middle.replace(/#amount-dr#/g, amount);
                    jQuery( row_middle ).insertAfter( jQuery("."+slug+".first") );
                }
            }
        }
    });

    calculate(slug);

    _jObj_attr = jQuery('[data-slug="'+slug+'"].cls_show_ans_box');
    if(_jObj_attr.length > 1){
        if(jQuery("."+slug+" td.dr").length > 2){
            _jObj_attr.removeClass("cls_show_ans_box").removeClass("link-dark");
            _jObj_attr.addClass("text-strikethrough");
        }
    }else{
        if(jQuery("."+slug+" td.dr").length == 2){
            _jObj_attr.removeClass("cls_show_ans_box").removeClass("link-dark");
            _jObj_attr.addClass("text-strikethrough");
        }
    }
}

function calculate(slug){
    if(jQuery("."+slug+" td.dr").length == 3){
        let cr = [];
        let dr = [];
        let re=/^[+-]?(?:\d*\.)?\d+$/;
        jQuery("."+slug+".dr").each(function(idx, itm){
            let amount = itm.innerHTML.trim();
            if(re.exec(amount)){
                amount = parseFloat(amount);
                dr.push(parseFloat(amount))
            }
        });

        jQuery("."+slug+".cr").each(function(idx, itm){
            let amount = itm.innerHTML.trim();
            if(re.exec(amount)){
                amount = parseFloat(amount);
                cr.push(parseFloat(amount))
            }
        });

        if(cr.length > 1){
            jQuery("."+slug+".first td.dr").text(cr[0]+cr[1]);
        }else{
            jQuery("."+slug+".last").prev().find("td.cr").text(dr[0]+dr[1]);
        }
    }
}

function make_dr_narration(tbl_name){
    return tbl_name + " " + ".".repeat(43-tbl_name.length-3)+" Dr";
}

function make_cr_narration(tbl_name){
    return "&nbsp;  &nbsp;  &nbsp; To "+tbl_name;
}
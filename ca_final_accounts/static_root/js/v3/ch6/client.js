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

    jQuery("body").on("click", ".cls_show_ans_box", function(e){
        e.preventDefault();
        e.stopPropagation();
        if ($(".cls_show_ans_box").hasClass("open")) {
            $(".cls_show_ans_box").removeClass("open");
        }
        let _this = jQuery(this);
        _this.addClass("open");
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
        let url = "/my-app/question/ch6/table/";
        jQuery.post(url, _jObj.XHR, function(res){
            switch(res.status){
                case "FAILURE":
                break;
                case "SUCCESS":
                    _data = res.data;
                    _data.sort((a, b) => (a.name > b.name) ? 1: -1);
                    _s_data = res.s_data;
                    let _sel_opt = "";
                    upon = _s_data.upon || "tbl2";
                    _upon_tbl = (upon === "tbl3")? 3 : 2;

                    _html2 = "";
                    _in_html = "";
                    res.s_data.header_cnt = res.s_data.header_cnt || {};
                    let _g_tbl_idx = 0;
                    jQuery.each(res.s_data.header_cnt, function(k, v){
                        if(k==="cr"){
                            _sel_opt = `<option>-:Select Credit A/c:-</option>`;
                        }else if(k === "dr"){
                            _sel_opt = `<option>-:Select Debit A/c:-</option>`;
                        }
                        _to = (k === "cr")? "To ": "";
                        _dr = (k === "dr")? " ... Dr": "";
                        _data.forEach(function(itm, idx){
                            _html2 = $app.data_store._html_first_table_option.replace(/#qun-slug#/g, _qun_slug);
                            _html2 = _html2.replace(/#slug#/g, _slug);
                            _html2 = _html2.replace(/#label#/g,
                                `${_to}${itm.name}${_dr}`);
                            _html2 = _html2.replace(/#code#/g, `${itm.code}#${k}#add`);
                            _html2 = _html2.replace(/#step#/g, `${itm.code}#${k}#add`);

                            if(itm.amount > 1){
                                _html2 = _html2.replace(/#amount#/g, _amount2);
                                _html2 = _html2.replace(/#position#/g, 2);
                            }else{
                                _html2 = _html2.replace(/#amount#/g, _amount);
                                _html2 = _html2.replace(/#position#/g, 1);
                            }
                            _sel_opt += _html2;
                        });

                        for(let i=0; i < v; i++){
                            _html1 = $app.data_store.id_html_qun_tbl.replace(/#index#/g, (_g_tbl_idx+1));
                            _g_tbl_idx += 1;
                            _html1 = _html1.replace(/#selectName#/g, (i+1));
                            _html1 = _html1.replace(/#selClass#/g, "cls_move_particular");
                            _html1 = _html1.replace(/#selectOption#/g, _sel_opt);

                            _in_html += _html1;
                        }
                    });

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

    jQuery(document).click(function (e) {
       if (!jQuery(e.target).parents().is(".tooltip-one")) {
          jQuery(".tooltiptext").remove();
          jQuery(".cls_show_ans_box").removeClass("open");
       }
    });
});

function answer_success_cb(data, _jObj, slug, position){
    if(_jObj[0].tagName == "OPTION"){
        _jObj = _jObj.parent();
    }
    let _correct = '<img src="/static/img/v3/success_icon.png" alt="check" width="15" class="mr-2" />correct';
    _jObj.parent().next().empty().append(_correct);
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
            add_history_row(itm.c_on, itm.element, itm.user_answer, itm.valid, itm.score, itm.answer_by, itm.hint);
        });
    }
}

function add_answered_row(slug, action_array, particular_name, amount, order_by, pair, table_name, position){
    let row_from_ac = '<tr class="#slug# first dataAddedHere"><td></td>';

    row_from_ac += '<td class="narration-1st">#from-a/c#</td>';

    row_from_ac += '<td>&nbsp;</td><td class="#slug# dr">#amount-dr#</td><td class="#slug# cr">#amount-cr#</td></tr>';
    row_from_ac += '#row-to-a/c#';
    row_from_ac += '<tr class="#slug# last dataAddedHere"><td></td><td class="narration-bottom-border">';
    row_from_ac += '(Being #b_transaction#)</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td></tr>';

    let row_to_ac = '<tr class="#slug# middle dataAddedHere"><td>';
    row_to_ac += '<span class="minus-but btn-next-element text-center d-block px-2 w-auto">Next</span></td>';
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

    if(jQuery("tbody tr").hasClass("dataAddedHere")) {
        let target = jQuery("tbody tr.dataAddedHere");
        // console.log(target.length);
        if(target.length){
            let scrollTo = target.offset().top;
            jQuery('body, html').animate({scrollTop: scrollTo+'px'}, 'slow');
        }
    }

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
    return `${tbl_name} ...Dr`;
//    return tbl_name + " " + ".".repeat(43-tbl_name.length-3)+" Dr";
}

function make_cr_narration(tbl_name){
    return "&nbsp;  &nbsp;  &nbsp; To "+tbl_name;
}

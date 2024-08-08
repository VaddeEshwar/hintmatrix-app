function calculate_profit_loss(){
    let tr_dr, tr_cr, loss, profit, pl_dr, pl_cr, bl_la, tr_dr_dom, tr_cr_dom, pl_dr_dom_loss, pl_dr_dom_profit,
    pl_cr_dom_loss, pl_cr_dom_profit, bs_ls_dom_profit, bs_ls_dom_loss;
    tr_dr = 0;
    tr_cr = 0;
    loss = 0;
    profit = 0;
    pl_dr = 0;
    pl_cr = 0;
    bl_la = 0;

    tr_dr_dom = jQuery(".tr-1-diff.profit");
    tr_cr_dom = jQuery(".tr-2-diff.loss");

    pl_dr_dom_loss = jQuery(".pl-1-diff.loss");
    pl_dr_dom_profit = jQuery(".pl-1-diff.profit");
    pl_cr_dom_loss = jQuery(".pl-2-diff.loss");
    pl_cr_dom_profit = jQuery(".pl-2-diff.profit");

    bs_ls_dom_loss = jQuery(".bs-1-diff.loss");
    bs_ls_dom_profit = jQuery(".bs-1-diff.profit");

    tr_dr_dom.empty();
    tr_cr_dom.empty();

    pl_dr_dom_profit.empty();
    pl_dr_dom_loss.empty();
    pl_cr_dom_profit.empty();
    pl_cr_dom_loss.empty();

    bs_ls_dom_loss.empty();
    bs_ls_dom_profit.empty();

    get_total_add("tr-1");
    get_total_add("tr-2");

    tr_dr = parse_html_float(jQuery(".tr-1-t")[0]);
    tr_cr = parse_html_float(jQuery(".tr-2-t")[0]);

    if (tr_dr > tr_cr){
        loss = parseFloat(tr_dr) - parseFloat(tr_cr);
        tr_cr_dom.text(loss);
        pl_dr_dom_loss.text(loss);
        get_total_add("tr-2");
        get_total_add("pl-1");
    }

    if(tr_cr > tr_dr){
        profit = parseFloat(tr_cr) - parseFloat(tr_dr);
        tr_dr_dom.text(profit);
        pl_cr_dom_profit.text(profit);
        get_total_add("tr-1");
        get_total_add("pl-2");
    }

    get_total_add("pl-1");
    get_total_add("pl-2");

    pl_dr = parse_html_float(jQuery(".pl-1-t"));
    pl_cr = parse_html_float(jQuery(".pl-2-t"));

    if(pl_dr > pl_cr){
        loss = parseFloat(pl_dr) - parseFloat(pl_cr);
        pl_cr_dom_loss.text(loss);
        loss *= -1;
        bs_ls_dom_loss.text(loss);
        get_total_add("pl-2");
        get_total_add("bs-1");
    }

    get_total_add("bs-1");
    get_total_add("bs-2");

    if(pl_cr > pl_dr){
        profit = parseFloat(pl_cr) - parseFloat(pl_dr);
        pl_dr_dom_profit.text(profit);
        bs_ls_dom_profit.text(profit);
        get_total_add("pl-1");
        get_total_add("bs-1");
    }
}

function get_total_add(cls){
    let val;
    let total = 0;
    jQuery("."+cls+"-a").each(function(idx, itm){
        val = parse_html_float(itm);
        if(!isNaN(val)){
            total += val;
        }
    });
    jQuery("."+cls+"-t").empty().append(total+"&nbsp;&nbsp;&nbsp;&nbsp;");
}

function add_answered_row(slug, action_array, particular_name, amount, order_by, pair){
    let _html_template = '<tr class="dataAddedHere" data-slug-pair="%SLUG%"><td>%PARTICULAR%</td>';
    _html_template += '<td class="%CLASS1% inner" data-particular-pair="%PAIR1%">';
    _html_template += '%AMOUNT1%</td><td class="%CLASS2% outer" data-particular-pair="%PAIR2%">';
    _html_template += '<div class="d-flex flex-column align-items-center"><span>%AMOUNT2%</span>';
    _html_template += '<span class="minus-but btn-next-element d-block px-2 w-auto">Next</span></div></td></tr>';

    let _fixed_particulars = jQuery("[data-fixed-particulars='y']");
    _fixed_particulars.empty();

    action_array.forEach(function(itm, idx){
        action = itm;
        action = action.split("#");
        let tbl = action[0];
        let particular = action[1];
        let add_sub = action[2];
        _tbl_cls = tbl + "-" + particular;

        _tbl = jQuery('[data-tbl-id="'+_tbl_cls+'"]');
        _tbl_id = _tbl.attr("id");
        _tbl_side = _tbl.attr("data-tbl-side");

        let dp_code = jQuery('a[data-slug="'+slug+'"]').attr("data-particular-code");
        if(dp_code){
            // for 2 places same element moved then only text-strickoff.
            if(jQuery('tr[data-slug-pair="'+slug+'"]').length > 0){
                _a = jQuery('a[data-slug="'+slug+'"]').removeClass("cls_show_ans_box").removeClass("link-dark");
                _a.addClass("text-strikethrough");
            }
        }else{
            _a = jQuery('a[data-slug="'+slug+'"]').removeClass("cls_show_ans_box").removeClass("link-dark");
            _a.addClass("text-strikethrough");
        }
        let class1 = _tbl_id+'-s';
        let class2 = _tbl_id+'-a';
        let amount1 = "";
        let amount2 = "";
        let pair1 = "";
        let pair2 = "";

        _pairs = _tbl.find('[data-particular-pair="'+pair+'"]');
        if(_pairs.length > 0){
            let _val, _total, _is_outer;
            pair1 = pair;
            _val = 0;
            _total = 0;
            _pairs.each(function(idx, itm_pair){
                _j_pair = jQuery(itm_pair);
                _val = parseFloat(_j_pair.text());
                if(!isNaN(_val)){
                    _total += _val;
                }
                _j_pair_inner = _j_pair.prev();
                if(_j_pair.hasClass("outer")){
                    _j_pair_inner.attr("data-particular-pair", pair);
                    _j_pair_inner.text(_val);

                    _j_pair.attr("data-particular-pair", "");
                    _j_pair.empty();
                }else if(_j_pair.hasClass("inner")){
                    _j_pair.next().empty();
                }

                if(add_sub == "sub"){
                    if(amount > 0){
                        amount *= -1;
                    }
                    if(!particular_name.includes("less:")){
                        particular_name = "less:"+ particular_name;
                    }
                }else{
                    particular_name = "add:"+ particular_name;
                }
            });
            _total = _total + amount;
            amount2 = _total;
            amount1 = amount;
            pair1 = pair;
        }else{
            // no pair exists
            if(add_sub == "sub"){
                pair1 = pair;
                amount1 = "-"+amount;
                particular_name = "less:"+ particular_name;
            }else{
                amount2 = amount;
                if(_tbl_side == "dr"){
                    particular_name = "to "+ particular_name;
                }else if(_tbl_side == "cr"){
                    particular_name = "by "+ particular_name;
                }
                pair2 = pair;
            }
        }

        let _h = _html_template.replace("%PARTICULAR%", particular_name);
        _h = _h.replace("%SLUG%", slug);
        _h = _h.replace("%CLASS1%", class1);
        _h = _h.replace("%CLASS2%", class2);
        _h = _h.replace("%AMOUNT1%", amount1);
        _h = _h.replace("%AMOUNT2%", amount2);
        _h = _h.replace("%PAIR1%", pair1);
        _h = _h.replace("%PAIR2%", pair2);

        jQuery("#"+_tbl_id+" tbody").append(_h);

        if(jQuery("#"+_tbl_id+" tbody tr").hasClass("dataAddedHere")) {
            let target = jQuery("#"+_tbl_id+" tbody tr").parent().parent().parent().parent().parent().parent().parent();
            if(target.length){
                let scrollTo = target.offset().top;
                jQuery('body, html').animate({scrollTop: scrollTo+'px'}, 'slow');
            }
        }

        get_total_add(_tbl_id);
        calculate_profit_loss();
    });
}


jQuery(function(){

    if(jQuery("#add-row-adjustments").length > 0){
        let clone_qun_fields = jQuery("#add-row-adjustments").html();
        $app.data_store["clone_qun_fields_adj"] = clone_qun_fields.replaceAll(/required=""/gim, "");
    }

    if(jQuery("#id_html_ans_box").length > 0){
        let id_html_ans_box = jQuery("#id_html_ans_box").html();
        $app.data_store["id_html_ans_box"] = id_html_ans_box.trim();
        jQuery("#id_html_ans_box").remove();
    }

    jQuery("body").on("click", ".cls_add_more_adj", function(e){
        e.preventDefault();
        jQuery("#add-row-adjustments").append($app.data_store.clone_qun_fields_adj);
    });

    jQuery("body").on("click", ".cls_show_ans_box", function(e){
        e.preventDefault();
        e.stopPropagation();
        if (jQuery(".cls_show_ans_box").hasClass("open")) {
            jQuery(".cls_show_ans_box").removeClass("open");
        }
        let _this = jQuery(this);
        _this.addClass("open");
        let _slug = _this.attr("data-slug");
        let _attr = _this.attr("data-attr");
        let _qun_slug = _this.attr("data-qun-slug");
        let _amount = _this.attr("data-amount");
        let _particular = _this.attr("data-particular");

        let _parent = _this.parent();
        jQuery(".tooltiptext").remove();
        let _html = $app.data_store.id_html_ans_box.replace(/#qun-slug#/g, _qun_slug);
        _html = _html.replace(/#slug#/g, _slug);
        _html = _html.replace(/%particular%/, _particular);
        _html = _html.replace(/%attribute%/, _attr);
        _html = _html.replace(/%amount%/, _amount);

        let answered_part = jQuery("a.cls_lbl.text-strikethrough").length;
        _html = _html.replace(/%no_of_element%/, answered_part);
        _html = _html.replace(/%total_elements%/, total_lbl);

        _parent.append(_html);
    });

    jQuery(document).click(function (e) {
       if (!jQuery(e.target).parents().is(".tooltip-one")) {
          jQuery(".tooltiptext").remove();
          jQuery(".cls_show_ans_box").removeClass("open");
       }
    });
});

function answer_failure_cb(res, _jObj){
    if(res.data[0].help){
        let _help1 = res["data"][0]["help"][0];

        let _help = '<table cellspacing="1" border="1" class="cls_tbl_hint"><tr><td class="option_bg_one" title="Selected option is wrong."><span class="hint_btn">Wrong</span></td>';
        _help += '<td class="cls_try_again option_bg_two" title="It allows to practice the same element again."><span class="hint_btn">Tryagain</span></td></tr>';
        _help += '<tr><td class="option_bg_three" title="It explains the concept in brief & guides the student to select the right option."><span class="hint_btn cls_show_hint" data-title="'+_help1+'">Hint</span></td>';
        _help += '<td class="option_bg_four" title="It automatically displays the answer in the solution table."><span class="hint_btn cls_auto_answer" ';
        _help += 'data-action="'+_jObj.XHR.action+'" data-slug="'+_jObj.XHR.slug+'" data-qun-slug="'+_jObj.XHR.qun_slug+'"';
        _help += '>Auto fill</span></td></tr></table>';

        jQuery(".cls_tbl_hint").hide('slow', function(){this.remove();});

        _jObj.parent().next().empty().append(_help);
    }else if(res.data[0].error){
        _jObj.parent().next().append(res.data[0].error[0]);
    }
    _history = res.data[0].history;
    if(_history){
        _history = JSON.parse(_history)
        _history.forEach(function(itm, idx){
            add_history_row(itm.c_on, itm.element, itm.user_answer, itm.valid, itm.score, itm.answer_by, itm.hint);
        });
    }
}

function answer_success_cb(data, _jObj, slug){
    let _correct = '<img src="/static/img/v3/success_icon.png" alt="check" width="15" class="mr-2" />correct';
    _jObj.parent().next().append(_correct);
    _data = data;
    action = _data.action;
    amount = _data.amount;
    slug = _data.slug;
    particular_name = jQuery('[data-slug="'+slug+'"].cls_lbl').text();

    add_answered_row(slug, action, particular_name, amount, data.order, data.pair);

    _history = _data.history;
    if(_history){
        _history = JSON.parse(_history)
        _history.forEach(function(itm, idx){
            add_history_row(itm.c_on, itm.element, itm.user_answer, itm.valid, itm.score, itm.answer_by, itm.hint);
        });
    }

//    let answered_part = jQuery("a.cls_lbl.text-strikethrough").length;
//    jQuery("a.cls_solved_total").text("solved / total particulars : "+answered_part+"/"+total_lbl);
}
// let total_lbl = jQuery("a.cls_lbl").length;
//jQuery("a.cls_solved_total").text("solved / total particulars : 0/"+total_lbl);

if(jQuery(".cls_amt1").length > 0 ){
    let total = 0, amt = 0;
    jQuery(".cls_amt1").each(function(idx, itm){
        amt = parseInt(itm.innerHTML);
        if(amt > 0){
            total += amt;
        }
    });
    jQuery(".cls_tot_amt1").text(total);
}


if(jQuery(".cls_amt2").length > 0 ){
    let total = 0, amt = 0;
    jQuery(".cls_amt2").each(function(idx, itm){
        amt = parseInt(itm.innerHTML);
        if(amt > 0){
            total += amt;
        }
    });
    jQuery(".cls_tot_amt2").text(total);
}

let total_lbl = jQuery("a.cls_lbl").length;

const replace_br = (txt) => { return txt.replace(/<br\/>/g, "\n"); };

function checkInteger(number) {
  let re = /^[+-]?(?:\d*\.)?\d+$/;
  if (re.exec(number)) {
    return true;
  }
  return false;
}

function parse_html_float(dom) {
  let val = parseFloat(jQuery(dom).text());
  if (!isNaN(val)) {
    return val;
  }
  return false;
}

function add_history_row(c_on, element, user_answer, valid, score, answer_by,
                         hint) {
  let _html_template =
      "<tr><td>%CNO%</td><td>%ELEMENT%</td><td>%OPTION%</td><td>%RESULT%</td>";
  _html_template += "<td>%ANSWERED%</td><td>%HINT%</td></tr>";

  let _h = _html_template.replace("%CNO%", new Date(c_on).toLocaleString());
  _h = _h.replace("%ELEMENT%", element);
  _h = _h.replace("%OPTION%", user_answer);

  let _status =
      '<img src="/static/img/v3/failed_icon.png" alt="wrong" width="15"/>';
  if (valid) {
    _status =
        '<img src="/static/img/v3/success_icon.png" alt="correct" width="15"/>' +
        "<br/>";
    _status += '<span class="cls_element_score">' + score + "</span>";
  }
  _h = _h.replace("%RESULT%", _status);
  _h = _h.replace("%ANSWERED%", answer_by);
  _h = _h.replace("%HINT%", hint);

  jQuery("#id_tbl_history tbody").prepend(_h);
  update_result();
}

function update_result() {
  const answered_part = jQuery("a.cls_lbl.text-strikethrough").length;
  let _t = "%no_of_element% Particulars Solved Out Of %total_elements%.";
  _t = _t.replace(/%no_of_element%/, answered_part);
  _t = _t.replace(/%total_elements%/, total_lbl);
  jQuery(".cls_qun_result").text(_t);
  /*
  if (total_lbl >0 and total_lbl === answered_part){
    console.log("answer complete");
  }
  */
  return;

  let total_score = 0;
  jQuery(".cls_element_score")
      .each(function(idx, itm) { total_score += parseFloat(itm.innerText); });
  let tot_ele = jQuery("a.cls_lbl.text-strikethrough").length;
  if (tot_ele < 1) {
    tot_ele = 1;
  }
  let tot_per = parseFloat((total_score / tot_ele) * 100).toFixed(2);
  jQuery(".cls_qun_result").text("Result : " + tot_per + "%");
}

function answer_failure_cb(res, _jObj) {
  if (_jObj[0].tagName == "OPTION") {
    let XHR = _jObj.XHR;
    _jObj = _jObj.parent();
    _jObj["XHR"] = XHR;
  }
  if (res.data[0].help) {
    let _help1 = res["data"][0]["help"][0];

    let _help =
        '<table cellspacing="1" border="1" class="cls_tbl_hint"><tr><td class="option_bg_one" title="Selected option is wrong."><span class="hint_btn">Wrong</span></td>';
    _help +=
        '<td class="cls_try_again option_bg_two" title="It allows to practice the same element again."><span class="hint_btn">Tryagain</span></td></tr>';
    _help +=
        '<tr><td class="option_bg_three" title="It explains the concept in brief & guides the student to select the right option."><span class="hint_btn cls_show_hint" data-title="' +
        _help1 + '">Hint</span></td>';
    _help +=
        '<td class="option_bg_four" title="It automatically displays the answer in the solution table."><span class="hint_btn cls_auto_answer" ';
    _help += 'data-action="' + _jObj.XHR.action + '" data-slug="' +
             _jObj.XHR.slug + '" data-qun-slug="' + _jObj.XHR.qun_slug + '"';
    _help += ">Auto fill</span></td></tr></table>";

    jQuery(".cls_tbl_hint").hide("slow", function() { this.remove(); });

    _jObj.parent().next().empty().append(_help);
  } else if (res.data[0].error) {
    _jObj.parent().next().empty().append(res.data[0].error[0]);
  }
  _history = res.data[0].history;
  if (_history) {
    _history = JSON.parse(_history);
    _history.forEach(function(
        itm,
        idx) { add_history_row(-1, itm.description, itm.valid, itm.action); });
  }
}

function answer_success_cb(data, _jObj, slug) {
  if (_jObj[0].tagName == "OPTION") {
    _jObj = _jObj.parent();
  }
  _jObj.parent().next().append("correct");
  _data = data;
  action = _data.action;
  amount = _data.amount;
  slug = _data.slug;
  particular_name = jQuery('[data-slug="' + slug + '"].cls_lbl').text();

  add_answered_row(slug, action, particular_name, amount, data.order,
                   data.pair);

  _history = _data.history;
  if (_history) {
    _history = JSON.parse(_history);
    _history.forEach(function(
        itm,
        idx) { add_history_row(-1, itm.description, itm.valid, itm.action); });
  }
}
jQuery(function() {
  if (jQuery("#add-row-question").length > 0) {
    let clone_qun_fields = jQuery("#add-row-question").html();
    $app.data_store["clone_qun_fields"] =
        clone_qun_fields.replaceAll(/required=""/gim, "");
  }

  jQuery("body").on("click", ".cls_add_more", function(e) {
    e.preventDefault();
    jQuery("#add-row-question").append($app.data_store.clone_qun_fields);
  });

  let fn_cls_mov_particular = function(e) {
    e.preventDefault();
    let _jObj = jQuery(this);
    if (e.target.tagName == "SELECT") {
      if (!_jObj.val() || _jObj.val().indexOf("-:Select") > -1) {
        return;
      }
      _jObj = jQuery(e.target.selectedOptions);
    }
    _jObj.XHR = {};
    _jObj.XHR.action = _jObj.attr("data-act");
    _jObj.XHR.slug = _jObj.attr("data-slug");
    _jObj.XHR.qun_slug = _jObj.attr("data-qun-slug");
    _jObj.XHR.amount = _jObj.attr("data-amount");
    /* for chapter 3; */
    _jObj.XHR.position = _jObj.attr("data-amount-position");
    _jObj.XHR.csrfmiddlewaretoken = jQuery("[name=csrfmiddlewaretoken]").val();
    let url = top.location.pathname;
    jQuery.post(url, _jObj.XHR, function(res) {
      switch (res.status) {
      case "FAILURE":
        answer_failure_cb(res, _jObj);
        break;
      case "SUCCESS":
        answer_success_cb(res.data[0], _jObj, _jObj.XHR.slug,
                          _jObj.XHR.position);
        break;
      }
    });
  };
  jQuery("body").on("click", "div.cls_move_particular", fn_cls_mov_particular);
  jQuery("body").on("change","select.cls_move_particular", fn_cls_mov_particular);

  jQuery("body").on("click", ".cls_auto_answer", function(e) {
    e.preventDefault();
    let _jObj = jQuery(this);
    _jObj.XHR = {};
    _jObj.XHR.slug = _jObj.attr("data-slug");
    _jObj.XHR.action = "auto#" + _jObj.attr("data-action");
    _jObj.XHR.qun_slug = _jObj.attr("data-qun-slug");
    _jObj.XHR.amount = _jObj.attr("data-amount");
    /* for chapter 3; */
    _jObj.XHR.position = _jObj.attr("data-amount-position");

    _jObj.XHR.csrfmiddlewaretoken = jQuery("[name=csrfmiddlewaretoken]").val();
    let url = top.location.pathname;
    jQuery.post(url, _jObj.XHR, function(res) {
      switch (res.status) {
      case "FAILURE":
        answer_failure_cb(res, _jObj);
        break;
      case "SUCCESS":
        answer_success_cb(res.data[0], _jObj, _jObj.XHR.slug);
        break;
      }
    });
  });

  // copy / delete / enable|disable
  jQuery("body").on("click", ".cls_question_action", function(e) {
    let _data = {_j : jQuery(e.currentTarget)};
    _data["action"] = _data._j.attr("data-action");
    _data["slug"] = _data._j.attr("data-question-slug");
    _data["chapter"] = _data._j.attr("data-chapter");
    $app.debug(_data);
    switch (_data["action"]) {
    case "copy":
      question_copy(_data["chapter"], _data["slug"]);
      break;
    case "enable":
      question_enable(_data["slug"], function(res) {});
      break;
    case "delete":
      question_delete(_data["slug"], function(res) {});
      break;
    }
    // copy => /my-app/ch3/slug/ edit mode of existing question
    // delete question
    // enable for all.
  });

  jQuery("body").on("click", ".cls_try_again", function(e) {
    e.preventDefault();
    jQuery(".cls_tbl_hint").remove();
  });

  jQuery("body").on("click", ".cls_lbl", function(e) {
    let target = jQuery(this);
    if (target.length) {
      let scrollTo = target.offset().top;
      jQuery("body, html").animate({scrollTop : scrollTo + "px"}, "slow");
    }
  });

  jQuery("body").on("click", ".cls_show_hint", function(e) {
    let _jObj = jQuery(e.currentTarget);
    if (_jObj.parent().find(".hint-box").length > 0) {
      jQuery(".hint-box").toggle(200);
    } else {
      let _title = _jObj.attr("data-title");
      _jObj.parent()
          .append("<div class='hint-box'>" + _title + "</div>")
          .show(200);
    }
  });

  jQuery("body").on("click", ".cls_reset_answer", function(e) {
    const url = top.location.pathname + "answered/";
    let _XHR = {};
    _XHR.csrfmiddlewaretoken = jQuery("[name=csrfmiddlewaretoken]").val();
    _XHR.reset = true;
    jQuery.post(url, _XHR,
                function(res) { top.window.location = top.location.pathname; });
  });

  if (window.load_history_or_events == true) {
    let _jObj = {};
    _jObj.XHR = {};
    _jObj.XHR.csrfmiddlewaretoken = jQuery("[name=csrfmiddlewaretoken]").val();
    let url = top.location.pathname;

    let load_history_or_events = () => {
      jQuery.post(url + "history/", _jObj.XHR, function(res) {
        if (res.status == "SUCCESS") {
          res.data.reverse().forEach(function(itm, idx) {
            add_history_row(itm.c_on, itm.element, itm.user_answer, itm.valid,
                            itm.score, itm.answer_by, itm.hint);
          });
        }
      });
    };

    jQuery.post(url + "answered/", _jObj.XHR, function(res) {
      if (res.status == "SUCCESS") {
        let _data = res.data;
        _data.forEach(function(itm, idx) {
          _jObj1 = jQuery('[data-slug="' + itm.slug + '"]');
          answer_success_cb(itm, _jObj1);
          jQuery(".table-five")
              .find(".dataAddedHere")
              .removeClass("dataAddedHere");
          jQuery(".table-five").find(".btn-next-element").remove();
        });
        load_history_or_events();
      }
    });
  }

  if (jQuery(".cls_lbl").parent().find(".tooltiptext")) {
    jQuery(document).on("click", "body", function(e) {
      jQuery(".table-five").find(".dataAddedHere").removeClass("dataAddedHere");
      jQuery(".table-five").find(".btn-next-element").remove();
      let nextTarget = jQuery(".cls_lbl")
                           .parent()
                           .find(".tooltiptext")
                           .parent()
                           .parent()
                           .parent();
      if (nextTarget.length) {
        let scrollTo = nextTarget.offset().top;
        jQuery("body, html").animate({scrollTop : scrollTo + "px"}, "slow");
      }
    });
  }

  jQuery("body").on(
      "click", "div#id_show_marks",
      function(e) { jQuery("div#id_show_table").toggleClass("show"); });
});

const question_delete = (slug, cb) => {
  const url = "/my-app/todo/" + slug + "/";
  let _XHR = {};
  _XHR.action = "delete";
  _XHR.csrfmiddlewaretoken = jQuery("[name=csrfmiddlewaretoken]").val();
  jQuery.post(url, _XHR,
              function(res) { top.window.location = top.location.pathname; });
};

const question_enable = (slug, cb) => {
  const url = "/my-app/todo/" + slug + "/";
  let _XHR = {};
  _XHR.action = "enable";
  _XHR.csrfmiddlewaretoken = jQuery("[name=csrfmiddlewaretoken]").val();
  jQuery.post(url, _XHR,
              function(res) { top.window.location = top.location.pathname; });
};

const question_copy = (chapter, slug) => {
  top.window.location = "/my-app/copy/" + chapter + "/" + slug + "/";
};

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

function add_history_row(idx, description, valid, action) {
  if (idx == -1) {
    idx = jQuery("#id_tbl_history tbody tr").length + 1;
  }

  let _html = "";
  let _html_template =
      "<tr><td>%SNO%</td><td>%DESC%</td><td>%VALID%</td><td>%ACTION%</td></tr>";
  _h = _html_template.replace("%SNO%", idx);
  _h = _h.replace("%DESC%", description);
  _h = _h.replace("%VALID%", valid);

  action = action ? action : "";
  _h = _h.replace("%ACTION%", action);
  _html += _h;

  jQuery("#id_tbl_history tbody").prepend(_html);
}

function answer_failure_cb(res, _jObj) {
  if (_jObj[0].tagName == "OPTION") {
    let XHR = _jObj.XHR;
    _jObj = _jObj.parent();
    _jObj["XHR"] = XHR;
  }
  if (res.data[0].help) {
    _help = '<abbr title="' + replace_br(res.data[0].help[0]) + '">hint</abbr>';
    _help += ' | <a href="javascript:void(0);" class="cls_auto_answer" ';
    _help += ' data-action="' + _jObj.XHR.action + '" ';
    _help += 'data-slug="' + _jObj.XHR.slug + '" data-qun-slug="' +
             _jObj.XHR.qun_slug + '">Auto route</a>';
    _jObj.parent().next().empty().append("!!!wrong<br/>" + _help);
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

  let body = jQuery("body");
  body.on("click", ".cls_add_more", function(e) {
    e.preventDefault();
    jQuery("#add-row-question").append($app.data_store.clone_qun_fields);
    jQuery("#add-row-question select").select2();
  });

  body.on("click", ".cls_move_particular", function(e) {
    e.preventDefault();
    let _jObj = jQuery(this);
    if (e.target.tagName == "SELECT") {
      if (_jObj.val() == "") {
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
  });
  body.on("click", ".cls_auto_answer", function(e) {
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
  body.on("click", ".cls_question_action", function(e) {
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

  body.on("click", "div#id_show_marks",
          function(e) { jQuery("div#id_show_table").toggleClass("show"); });


  body.on("click", "#id_copy_text", function(e) {
    let _this = e.target;
    _this.select();
    document.execCommand("copy");
  });

  body.on("click", "#id_copy_link", (e)=>{
    jQuery("#id_copy_text").trigger("click");
  });

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

if (window.load_history_or_events == true) {
  var _jObj = {};
  _jObj.XHR = {};
  _jObj.XHR.csrfmiddlewaretoken = jQuery("[name=csrfmiddlewaretoken]").val();
  let url = top.location.pathname + "history/";

  jQuery.post(url, _jObj.XHR, function(res) {
    if (res.status == "SUCCESS") {
      let _data = res.data;
      let _html = "";
      // date, element, option selected / result / answered by / hint
      let _html_template =
          "<tr><td>%SNO%</td><td>%DESC%</td><td>%VALID%</td><td>%ACTION%</td>";
      _html_template += "<td>ans by</td><td>hint</td></tr>";
      let _len = _data.length;
      _data.forEach(function(itm, idx) {
        _h = _html_template.replace("%SNO%", _len - idx);
        _h = _h.replace("%DESC%", itm.description);
        _h = _h.replace("%VALID%", itm.valid);

        itm.action = itm.action ? itm.action : "";
        _h = _h.replace("%ACTION%", itm.action);
        _html += _h;
      });
      jQuery("#id_tbl_history tbody").append(_html);
    }
  });

  url = top.location.pathname + "answered/";
  jQuery.post(url, _jObj.XHR, function(res) {
    if (res.status == "SUCCESS") {
      let _data = res.data;
      _data.forEach(function(itm, idx) {
        _jObj1 = jQuery('[data-slug="' + itm.slug + '"]');
        answer_success_cb(itm, _jObj1);
      });
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
}

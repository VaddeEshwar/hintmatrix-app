// add qustion start
String.prototype.compose = (function (){
    var re = /\{{(.+?)\}}/g;
    return function (o){
        return this.replace(re, function (_, k){
            return typeof o[k] != 'undefined' ? o[k] : '';
        });
    }
}());

function ConvertFormToJSON(frm){
    let _array = jQuery(frm).serializeArray();
    let _json = {};

    jQuery.each(_array, function(idx, itm) {
        _json[itm.name] = itm.value || '';
    });

    return _json;
}

function fun_refresh_token(){
    let _obj = {};
    _obj.SRC = "/api/v1/token/refresh/";
    _obj.DATA = {
        "refresh": get_s_key('refresh')
    };
    $app.io.makeRequest(_obj, function(r){
        remove_s_key('access');
        set_s_key('access', r.access);
        $app.sec.access = r.access;
    });
}

function UUID4(){
    let dt = new Date().getTime();
    let uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g,
    function(c) {
        let r = (dt + Math.random()*16)%16 | 0;
        dt = Math.floor(dt/16);
        return (c=='x' ? r :(r&0x3|0x8)).toString(16);
    });
    return uuid;
}

function set_s_key(key, value){
    if (typeof(Storage) !== "undefined"){
        localStorage.setItem(key, value);
    }else{
        $app.debug(arguments);
    }
}

function get_s_key(key){
    let _val = void 0;
    if (typeof(Storage) !== "undefined"){
        _val = localStorage.getItem(key);
    }else{
        $app.debug(arguments);
    }
    return _val;
}

function remove_s_key(key){
    if (typeof(Storage) !== "undefined"){
        localStorage.removeItem(key);
    }else{
        $app.debug(arguments);
    }
}

function get_attributes(cb){
    let _a = get_s_key('attributes')
    if(_a != null){
        _a = JSON.parse(_a);
        cb(_a);
        return true;
    }
    let _obj = {};
    _obj.METHOD = 'GET';
    _obj.SRC = "/api/v1/question/attributes/";
    $app.io.makeRequest(_obj, function(r){
        remove_s_key('attributes');
        set_s_key('attributes', JSON.stringify(r.data));
        cb(r.data);
    });
}

function populate_attributes(sel_cls){
    get_attributes(function(_attr){
        _attr = [{"code":"","name":"-- Please choose an option --",
        "s_name":"-- Please choose an option --"}].concat(_attr);
        if(sel_cls == void 0){
            sel_cls = "select.sel_attr";
        }
        jQuery(sel_cls).html(
        jQuery.map(_attr, function(itm, _ix){
          return '<option value="' + itm['code'] + '">'+ itm['s_name']
          +'</option>';
        }).join("") );
    });
}

/*
{
        "title": "title 124",
        "dr_attr_code": ["<attr_code>", "<attr_code>"],
        "dr_amount": [
            34.56, 78.67
        ],
        "cr_attr_code": [
            "<attr_code>", "attr06"
        ],
        "cr_amount": [
            7890.45, 23456.56
        ],
        "adj_attr_code": ["<attr_code>", "attr04"],
        "adj_amount": [345.67, 6789.54]
    }

*/
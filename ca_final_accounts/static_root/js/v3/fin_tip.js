function fin_tip() {
   let _self = this;
   _self.debug = function () {
      try {
         console.log(arguments);
      } catch (e) {}
   };

   _self.io = {};
   _self.io.json_parser = JSON.parse;
   _self.io.makeRequest = function (obj, callback) {
      obj = obj || {};
      callback = callback || function () {};
      obj.METHOD = obj.METHOD || "POST";
      obj.DATA = obj.DATA || "";
      obj.SRC = obj.SRC || "";
      obj.DATATYPE = obj.DATATYPE || "json";
      obj.SCRIPT_CHARSET = obj.SCRIPT_CHARSET || "utf-8";
      obj.CACHE = obj.CACHE || false;
      obj.PROCESS_DATA = obj.PROCESS_DATA == void 0 ? true : obj.PROCESS_DATA;
      let _c_type = "application/x-www-form-urlencoded; charset=UTF-8";
      obj.CONTENT_TYPE = obj.CONTENT_TYPE != void 0 ? obj.CONTENT_TYPE : _c_type;
      if (obj.ASYNC == void 0) {
         obj.ASYNC = true;
      }
      obj.COMPLETE = obj.COMPLETE || function () {};

      obj.BEFORE_SEND_DEFAULT = function (request) {
         if (get_s_key("access") !== void 0) {
            request.setRequestHeader("Authorization", "JWT " + get_s_key("access"));
         }
         request.setRequestHeader("Request-Id", UUID4());
      };
      obj.BEFORE_SEND = obj.BEFORE_SEND || obj.BEFORE_SEND_DEFAULT;
      obj.CALLBACK400 = obj.CALLBACK400 || function () {};
      obj.CALLBACK201 = obj.CALLBACK201 || function () {};
      obj.CALLBACK500 = obj.CALLBACK500 || function () {};
      obj.CALLBACK403 = obj.CALLBACK403 || function () {};
      obj.CALLBACK_ERROR = obj.CALLBACK_ERROR || function () {};
      $app.debug(obj.SRC, obj.METHOD, obj.DATA);
      obj.getAllResponse = $.ajax({
         method: obj.METHOD,
         url: obj.SRC,
         data: obj.DATA,
         dataType: obj.DATATYPE,
         contentType: obj.CONTENT_TYPE,
         scriptCharset: obj.SCRIPT_CHARSET,
         cache: obj.CACHE,
         async: obj.ASYNC,
         processData: obj.PROCESS_DATA,
         beforeSend: obj.BEFORE_SEND,
         success: function (r) {
            $app.debug(r);
            callback(r);
         },
         complete: function (r) {
            switch (r.status) {
               case 200:
                  break;
               case 201:
                  obj.CALLBACK201(r);
                  break;
               case 403:
                  obj.CALLBACK403(r);
                  break;
               case 500:
                  obj.CALLBACK500(r);
                  break;
               case 400:
                  obj.CALLBACK400(r);
                  break;
            }
            obj.COMPLETE(r);
         },
         error: obj.CALLBACK_ERROR,
      });
   };
}
var $app = new fin_tip();
$app.data_store = {};
$app.debug($app);

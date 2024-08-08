$app.data_store = {};

jQuery(function(){

    if(jQuery("#question_create").length > 0){
        $app.data_store["clone_qun_fields"] = jQuery("#question_create").html();
    }

    jQuery("body").on("click", ".cls_add_more", function(e){
        e.preventDefault();
        jQuery("#question_create").append($app.data_store.clone_qun_fields);
    });


    jQuery("body").on("change", ".cls_cp_action", function(e){
        e.preventDefault();
        jQuery(".cls_invalid_match").remove();
        let jObj = jQuery(this);
        let html = "";
//        console.log(jObj);
        jObj.XHR = {};
        jObj.XHR.h = jObj.val();
        let txt = jObj.find("option:selected").text().trim();
        jObj.XHR.txt = txt;

        let parent = jObj.parent();
        let previous = $(parent).parent().prev();
        jObj.XHR.a = previous.attr("data-id");

        let value = $(parent).parent().next().text();
        value = parseFloat(value);

        /*
        make a call to server to store as well check rule is valid?
        */

        // console.log(jObj.XHR);
        let url = top.location.href;
        url = top.location.pathname;
        jObj.XHR.csrfmiddlewaretoken = jQuery("[name=csrfmiddlewaretoken]").val();
        jQuery.post(url, jObj.XHR, function(res){
            if(res.SUCCESS){
//                console.log(res);
                let tbl_id = fun_make_id(txt);
                let value_cls = fun_make_val_css(txt);
                console.log(tbl_id, value_cls)
                let attribute = $(previous).text();
                html = '<div class="debit-wrapper-body row values no-mar">';
                html += '<div class="col-sm-6 col-xs-6 no-pad">';
                html += '<div class="form-field">'+attribute+'</div></div>';
                html += '<div class="col-sm-6 col-xs-6 no-pad">';
                html += '<div class="form-field '+value_cls+'">'+value;
                html += '</div></div></div>';

//                html = "<tr><td>"+attribute+"</td><td>&nbsp;</td>";
//                html +="<td class='"+value_cls+"'>"+value+"</td>";

                jQuery("#"+tbl_id).append(html);

                let tot_val = 0;
                console.log(jQuery("."+value_cls));
                jQuery("."+value_cls).each(function(index, item){
                    tot_val += parseFloat(item.innerHTML)
                });
                let tot_id = fun_tot_make_id(txt);
                console.log(tot_id);
                jQuery("#"+tot_id).text(tot_val);

            }else{
                let msg = "<div class='cls_invalid_match'>Invalid!!!\n"+res.msg+"</div>";
                parent.append(msg);
            }
        });
    });
});

let fun_make_id = function(txt){
    txt = txt || "";
    txt = txt.split("-");
    t1 = txt[0].split(" ");
    t11 = t1[0].toLowerCase();
    t2 = txt[1].split(" ");
    t22 = t2[0].toLowerCase();

    if(["libilities", "debit"].indexOf(t22) > -1 ){
        t22 = "dr"
    }

    if(["asset", "credit"].indexOf(t22) > -1 ){
        t22 = "cr"
    }

    return "id_tbl_"+t11+"_"+t22;
}

let fun_make_val_css = function(txt){
    txt = txt || "";
    txt = txt.split("-");
    t1 = txt[0].split(" ");
    t11 = t1[0].toLowerCase();
    t2 = txt[1].split(" ");
    t22 = t2[0].toLowerCase();
    if(["libilities", "debit"].indexOf(t22) > -1 ){
        t22 = "dr"
    }

    if(["asset", "credit"].indexOf(t22) > -1 ){
        t22 = "cr"
    }

    return "cls_tbl_val_"+t11+"_"+t22;
}

let fun_tot_make_id = function(txt){
    txt = txt || "";
    txt = txt.split("-");
    t1 = txt[0].split(" ");
    t11 = t1[0].toLowerCase();
    t2 = txt[1].split(" ");
    t22 = t2[0].toLowerCase();

    if(["libilities", "debit"].indexOf(t22) > -1 ){
        t22 = "dr"
    }

    if(["asset", "credit"].indexOf(t22) > -1 ){
        t22 = "cr"
    }

    return "id_td_tot_"+t11+"_"+t22;
}

/* Set the width of the side navigation to 250px */
function openNav() {
    document.getElementById("mySidenav").style.width = "250px";
  }
  
  /* Set the width of the side navigation to 0 */
  function closeNav() {
    document.getElementById("mySidenav").style.width = "0";
  }

function openMenu() {
  var x = document.getElementById("myTopnav");
  if (x.className === "menu") {
    x.className += " responsive";
  } else {
    x.className = "menu";
  }
}

function dragMoveListener (event) {
  var target = event.target
  // keep the dragged position in the data-x/data-y attributes
  var x = (parseFloat(target.getAttribute('data-x')) || 0) + event.dx
  var y = (parseFloat(target.getAttribute('data-y')) || 0) + event.dy

  // translate the element
  target.style.webkitTransform =
    target.style.transform =
      'translate(' + x + 'px, ' + y + 'px)'

  // update the posiion attributes
  target.setAttribute('data-x', x)
  target.setAttribute('data-y', y)
}

// this is used later in the resizing and gesture demos
//window.dragMoveListener = dragMoveListener
/* Drag and Drop */
/* The dragging code for '.draggable' from the demo above
 * applies to this demo as well so it doesn't have to be repeated. */

// enable draggables to be dropped into this
//interact('.dropzone').dropzone({
//  // only accept elements matching this CSS selector
//  accept: '.drag-drop',
//  // Require a 75% element overlap for a drop to be possible
//  overlap: 0.75,
//
//  // listen for drop related events:
//
//  ondropactivate: function (event) {
//      const item = event.relatedTarget
//      item.classList.add('dragging')
//    },
//    ondropdeactivate: function (event) {
//      const item = event.relatedTarget
//      item.classList.remove('dragging', 'cannot-drop')
//    },
//    ondragenter: function(event) {
//      const item = event.relatedTarget
//      item.classList.remove('cannot-drop')
//      item.classList.add('can-drop')
//    },
//    ondragleave: function(event) {
//      const item = event.relatedTarget
//      item.classList.remove('can-drop')
//      item.classList.add('cannot-drop')
//    }
//})
//
//interact('.drag-drop')
//  .draggable({
//    inertia: true,
//    modifiers: [
//      interact.modifiers.restrictRect({
//        restriction: '.credit',
//        endOnly: true
//      })
//    ],
//    autoScroll: true,
//    // dragMoveListener from the dragging demo above
//    onmove: dragMoveListener
//  })

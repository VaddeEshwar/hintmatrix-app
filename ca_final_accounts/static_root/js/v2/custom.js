// add qustion start 
String.prototype.compose = (function (){
    var re = /\{{(.+?)\}}/g;
    return function (o){
        return this.replace(re, function (_, k){
            return typeof o[k] != 'undefined' ? o[k] : '';
        });
    }
}());

var tbody = $("#myTable").children("tbody");
var table = tbody.length ? tbody : $("#myTable");
var row = "<tr>" + "<td>{{id}}</td>" + "<td>{{name}}</td>" + "<td>{{gender}}</td>" + "<td>{{phone}}</td>" + "</tr>";

var tbody = $('#myTable').children('tbody');
var table = tbody.length ? tbody : $('#myTable');
var row = '<tr>'+
    '<td>{{id}}</td>'+
    '<td>{{name}}</td>'+
    '<td>{{gender}}</td>'+
	'<td>{{phone}}</td>'+
'</tr>';


$('button.addthis').click(function(){
    
    //Add row
    table.append(row.compose({
        'id': '<select id="#" class="select-one"><option value="0">-- Please choose an option --</option><option value="28">advertising</option><option value="42">audit charge</option><option value="36">bad debts</option><option value="68">bills payable</option><option value="65">bills receivabl</option><option value="4">capital</option><option value="8">carriage</option><option value="10">carriage inward</option><option value="38">carriage on sal</option><option value="23">carriage outwar</option><option value="63">cash</option><option value="9">clearing charge</option><option value="62">closing stock</option><option value="6">closing stock</option><option value="17">coal and water</option><option value="30">commission</option><option value="47">commission rece</option><option value="57">copy right</option><option value="66">credit</option><option value="67">creditors</option><option value="20">customs duty</option><option value="61">debentures of o</option><option value="64">debtors</option><option value="37">depreciation</option><option value="31">discount</option><option value="29">discount allowe</option><option value="45">discount receiv</option><option value="49">dividend receiv</option><option value="72">drawings (less </option><option value="11">factory insuran</option><option value="15">factory lightin</option><option value="21">factory rent</option><option value="59">fixed deposit</option><option value="12">frieght</option><option value="13">frieght inwards</option><option value="24">frieght outward</option><option value="50">furniture</option><option value="55">good will</option><option value="19">import duties</option><option value="48">interest receiv</option><option value="52">land and buildi</option><option value="41">legal expenses</option><option value="69">loan</option><option value="51">machinery</option><option value="18">manufacturing e</option><option value="71">net loss (less </option><option value="70">net profit (add</option><option value="44">office rent</option><option value="16">oil and fuel</option><option value="5">opening stock</option><option value="56">paytent</option><option value="53">plant and machi</option><option value="34">postage</option><option value="54">premises</option><option value="1">purchases</option><option value="26">rent</option><option value="32">rent and taxes</option><option value="46">rent received</option><option value="40">repairs</option><option value="2">return inwards </option><option value="22">return outwards</option><option value="25">salaries</option><option value="33">salaries and wa</option><option value="3">sales</option><option value="60">shares of other</option><option value="27">stationery</option><option value="43">telephone charg</option><option value="39">trade expenses</option><option value="58">trade mark</option><option value="35">travelling expe</option><option value="7">wages</option><option value="14">wages and salar</option></select>',
        'name': '<input type="number" id="quantity" name="quantity" min="0" class="inp-num">',
		'gender': '<select id="#" class="select-one"><option value="0">-- Please choose an option --</option><option value="28">advertising</option><option value="42">audit charge</option><option value="36">bad debts</option><option value="68">bills payable</option><option value="65">bills receivabl</option><option value="4">capital</option><option value="8">carriage</option><option value="10">carriage inward</option><option value="38">carriage on sal</option><option value="23">carriage outwar</option><option value="63">cash</option><option value="9">clearing charge</option><option value="62">closing stock</option><option value="6">closing stock</option><option value="17">coal and water</option><option value="30">commission</option><option value="47">commission rece</option><option value="57">copy right</option><option value="66">credit</option><option value="67">creditors</option><option value="20">customs duty</option><option value="61">debentures of o</option><option value="64">debtors</option><option value="37">depreciation</option><option value="31">discount</option><option value="29">discount allowe</option><option value="45">discount receiv</option><option value="49">dividend receiv</option><option value="72">drawings (less </option><option value="11">factory insuran</option><option value="15">factory lightin</option><option value="21">factory rent</option><option value="59">fixed deposit</option><option value="12">frieght</option><option value="13">frieght inwards</option><option value="24">frieght outward</option><option value="50">furniture</option><option value="55">good will</option><option value="19">import duties</option><option value="48">interest receiv</option><option value="52">land and buildi</option><option value="41">legal expenses</option><option value="69">loan</option><option value="51">machinery</option><option value="18">manufacturing e</option><option value="71">net loss (less </option><option value="70">net profit (add</option><option value="44">office rent</option><option value="16">oil and fuel</option><option value="5">opening stock</option><option value="56">paytent</option><option value="53">plant and machi</option><option value="34">postage</option><option value="54">premises</option><option value="1">purchases</option><option value="26">rent</option><option value="32">rent and taxes</option><option value="46">rent received</option><option value="40">repairs</option><option value="2">return inwards </option><option value="22">return outwards</option><option value="25">salaries</option><option value="33">salaries and wa</option><option value="3">sales</option><option value="60">shares of other</option><option value="27">stationery</option><option value="43">telephone charg</option><option value="39">trade expenses</option><option value="58">trade mark</option><option value="35">travelling expe</option><option value="7">wages</option><option value="14">wages and salar</option></select>',
        'phone': '<input type="number" id="quantity" name="quantity" min="0" class="inp-num">'
    }));
})

// end add qustion 

// start slider
$('.example-1').square1({caption: 'none',
	theme: 'light'});
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



// open and close 
function openForm() {
  document.getElementById("myForm").style.display = "block";
}

function closeForm() {
  document.getElementById("myForm").style.display = "none";
}




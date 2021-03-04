import { jsPDF } from "jspdf";
alert("Hello");
var doc = new jsPDF();
var elementHTML = $('#main').html();
doc.text(elementHTML,40,40);

/*var specialElementHandlers = {
    '#editor': function (element, renderer) {
        return true;
    }
};
doc.fromHTML(elementHTML, 15, 15, {
    'width': 170,
    'elementHandlers': specialElementHandlers
});*/

// Save the PDF
doc.save('sample-document.pdf');

//window.onload = function() {
//  var minute =3;
//  var sec = 60;
//  setInterval(function() {
//    document.getElementById("time").innerHTML = minute + " : " + sec;
//    sec--;
//    if (sec == 00) {
//      minute --;
//      sec = 60;
//
//    }
//  }, 1000);
//}

 //document.getElementById("time")
 var myVar;
       var timer = document.getElementById("time");
       console.log(timer)
       var countDownSeconds;
       function startTime(){
         myVar = setInterval(start, 1000);
         document.getElementById("time").innerHTML = timer.value;
         console.log(timer.value);
         countDownSeconds = timer.value;
       }

       function start(){
         countDownSeconds--;
         document.getElementById("time").innerHTML = countDownSeconds;
         if (countDownSeconds == -1){
           stop();
           document.getElementById("time").innerHTML = "0";
         }
       }

       function stop(){
         clearInterval(myVar);
       }
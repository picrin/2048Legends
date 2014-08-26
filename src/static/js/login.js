$(window).load(function(){
  window.Csrf2048wc.setupCSRF();
});
$("#submit").click(window.Crypto2048wc.submitClick);
$(document).keydown(function(key){
  if(key.which == 13){
    $("#submit").click();
  }
});
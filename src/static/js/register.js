$(window).load(function(){
  window.Csrf2048wc.setupCSRF();
});
$("#submit").click(window.Crypto2048wc.register);
$(document).keydown(function(key){
  if(key.which == 13){
    $("#submit").click();
  }
});
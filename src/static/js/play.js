//Copyright (c) Adam Kurkiewicz 2014, all rights reserved.

//Please mind that currently any derivative work or unauthorized use is
//prohibited. This code is expected to be released under permissive licence
//after the competition. Currently it is shared for review purpose only.

$(document).ready(function(){
  window.Csrf2048wc.setupCSRF();
  var userid = 1029123;
  window.Play2048wc.DOMready(userid);
});
$(document).keydown(function(key){
  var direction = window.Play2048wc.input(key);
  if (direction !== null){
    var serverCommitment = window.Play2048wc.clientCommitment(direction, "16dc368a89b428b2485484313ba67a3912ca03f2b2b42429174a4f8b3dc84e44");
    console.log(serverCommitment);
  }
});



//Copyright (c) Adam Kurkiewicz 2014, all rights reserved.

//Please mind that currently any derivative work or unauthorized use is
//prohibited. This code is expected to be released under permissive licence
//after the competition. Currently it is shared for review purpose only.

$(window).load(function(){
  window.Csrf2048wc.setupCSRF();
  window.Play2048wc.orderBoard();

});

var swipeOrKey = function(direction){
  //var serverCommitment = window.Play2048wc.clientCommitment(direction, );
  var r$h = window.Crypto2048wc.randomWithHash();
  window.Play2048wc.negotiateMove(direction, r$h.random, r$h.randomHash);
};

$(document).keydown(function(key){
  var direction = window.Play2048wc.input(key);
  if (direction !== null){
    swipeOrKey(direction);
  }
});

//n.clientCommitment = function(direction, commitment)

$("#gameboard").swipe({
  swipe:function(event, direction, distance, duration, fingerCount) {
    if ($.inArray(direction, ["up", "down", "left", "right"] !== -1)){
      swipeOrKey(direction);
    }
  },
  threshold:15
});

$(window).resize(window.Play2048wc.onResize);
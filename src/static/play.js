//Copyright (c) Adam Kurkiewicz 2014, all rights reserved.

//Please mind that currently any derivative work or unauthorized use is
//prohibited. This code is expected to be released under permissive licence
//after the competition. Currently it is shared for review purpose only.


//------------------------- GLOBAL NUMERICAL CONSTANTS -------------------------
var boardSize = 4;
var gapSize = 10; //currently in pxs, might migrate to something more reasonable
var tileSize = 80 + gapSize; // vide supra
var quick = 200; //ms


//------------------------------- DIV CONSTANTS -------------------------------
//global constants of divs we'll be appending to and removing from.
//id of div to keep tiles inside, most of work will be done on this div.
var tiles = "#tiles";
//id of div to keep slots inside
var slots = "#tile-placeholders";
//id of bin -- place which should be emptied every next move.
var bin = "#garbage";


//--------------------------------- TEMPLATES ---------------------------------
//A few Mustache templates follow, gutted there's just no better place to keep
//them (a separate file would be ideal)

//Template for tiles
var tile_template ='\
<div {{idtype}}="row{{rowNo}}col{{colNo}}"class="tile" style="left: {{leftpx}}px; top: {{toppx}}px;">\
  {{value}}\
</div>\
';

//Template for slots
var slot_template = '\
<div class="tile-placeholder" style="left: {{leftpx}}px; top: {{toppx}}px;">\
</div>\
';

//template for attributes: id and data-nextid
var IDTemplate = "row{{row_i}}col{{col_i}}";
//wee template for pxs.
var valuepx = "{{value}}px";


//------------------------------ HELPER FUNCTIONS ------------------------------
// id of the form "row0col1"
function extractRowCol(id){
  return [id[3], id[7]];
}

//this computes a relative coordinate in units (px, but I might migrate to
//something more relative).
function coordinate(index){
  return tileSize * index + gapSize;
}

//this returns a jquery with a tile.
function getTile(coords){
  var tileID = Mustache.render("#" + IDTemplate, {"row_i": coords[0], "col_i": coords[1]});
  return $(tileID);
}

//this is a pure function. Creates HTML nicely styled with css, which can be
//furhter worked on or appended to the appropriate div. Notice how properties
//left, top and id are in fact treated as variables, as they keep the state of
//the program. 
function createTileHTML(rowNo, colNo, board, real){
  var idType = null;
  if (real){
    idType = "id";
  }
  else{
    idType = "data-nextid";
  }
  var values = {
    idtype: idType,
    value: board[rowNo][colNo],
    leftpx: coordinate(colNo),
    toppx: coordinate(rowNo),
    rowNo: rowNo,
    colNo: colNo,
  }
  return Mustache.render(tile_template, values);
}

//iterate over every move, and call a func(from, to), where from and to are
//syntactically arrays of length two, and semantically coordinates.
function eachMove(moves, func){
  $.each(moves, function(row_i, rows){
    $.each(rows, function(col_i, newpos){
      func([row_i, col_i], newpos);
    });
  });
}

//call a func(index, jquery, board), for every element in tiles div
function eachSlot(func, board){
  $(tiles).children().each(function(index, jquery){
    //console.lo
    //func(index, jquery, board);
  });
}



//------------------------------ LAYOUT FUNCTIONS ------------------------------
//These two functions modify appropriate DOM elements adding html and css
//to make a game board from it (with slots and tiles and shit).
function prepareSlots(){
  $(slots).empty();
  for (var i = 0; i < boardSize; i++){
    for (var ii = 0; ii < boardSize; ii++){
        var values = {
          leftpx: coordinate(i),
          toppx: coordinate(ii),
        }
        var slot_html = Mustache.render(slot_template, values);
        $(slots).append(slot_html);
    }
  }
}
function appendTiles(board){
  $(tiles).empty();
  //loop through columns
  for (var i = 0; i < boardSize; i++){
    //loop through rows, 
    for (var ii = 0; ii < boardSize; ii++){
      if (board[i][ii] != 0){
        var tile_html = createTileHTML(i, ii, board, true);
        $(tiles).append(tile_html);
      }
    }
  }
}

function appendTile(x, y, board){
  var tile = $(createTileHTML(x, y, board, false));
  $(tiles).append(tile);
  tile.hide().delay(quick/2).fadeIn(quick/2);
}


//----------------------------- ON-CLICK MACHINERY -----------------------------
//A little bit of currying to fit in our func(from, to) framework.
function moveTile(board){
  return function(from, to){
    _moveTile(from, to, board);
  }
}

//pass 2 arrays and a board, like moveTile([1,3], [1, 0], b);
function _moveTile(from, to, board){
  var fromTile = getTile(from);
  var leftpx = Mustache.render(valuepx, {value: coordinate(to[0])});
  var toppx = Mustache.render(valuepx, {value: coordinate(to[1])});
  //currently we have no good way of applying post-animation function to the
  //tile that needs it, so we apply it to all tiles. Can be further worked on.
  fromTile.animate({top: leftpx, left: toppx}, quick, function(){
    $(bin).empty();
    stateAtIndex(true, false)(to, board);
  });
}

function preRename(from, to){
  //this is so poorly designed, probably it would be better to keep DOM elements
  //in a js object rather then using html ids and data attributes. That might be
  //a good TODO, in case I'd want to improve my javascript.
  var tilefrom = getTile(from);
  var newTileID =  Mustache.render(IDTemplate, {"row_i": to[0], "col_i": to[1]});
  tilefrom.attr("data-nextid", newTileID); 
}

function postRenameAll(board){
  var children = $(tiles).children();
  $.each(children, function(_, childHTML){
    var nextID = childHTML.getAttribute("data-nextid");
    if (nextID !== null){
      childHTML.removeAttribute("data-nextid");
      childHTML.id = nextID;
    }
  });

}

function removeTile(coords, _){
  var tile = getTile(coords);
  tile.removeAttr('id');
  tile.detach();
  $(bin).append(tile);
}


//----------------------- NETWORK/ KEYBOARD IO FUNCTIONS -----------------------
function nextMove(directioncode){
  var board_data = null;
  $.ajax({
    type: 'POST',
    url: 'nextmove',
    data: {gameid: "12q345908762459876", direction: directioncode},
    async: false,
    success: function(data){
      board_data = data;
    }
  });
  return board_data;
}

function orderBoard(){
  var board = null;
  $.ajax({
    type: 'GET',
    url: 'get_board',
    data: {userid: "dupa"},
    async: false,
  }).done( function(data){
    board = data["board"];
  });
  return board;
}

//Copy-paste from SO, I do not own the copyright
function input(key){
    var direction = null;
    switch(key.which){
      case 37: // left
        direction = 3;
      break;
      case 38: // up
        direction = 0;
      break;
      case 39: // right
        direction = 1;
      break;
      case 40: // down
        direction = 2;
      break;
    }
    if (direction != null){
      key.preventDefault(); // prevent the default action (scroll / move caret)
    }
    return direction;
}


//------------------------------- STATE RECOVERY -------------------------------
//HTML/CSS is a rather poor place to keep our state in. It is understood that
//such state can get broken any time, and thus should be closely watched and
//repaired when necessary.

function stateAtJQuery(repair, warn){
  return function(jQuery, board){
    _stateAtJQuery(jQuery, board, repair, warn);
  }
}

function stateAtIndex(repair, warn){
  return function(index, board){
    _stateAtIndex(index, board, repair, warn);
  }
}

function _stateAtIndex(index, board, repair, warn){
  var query = getTile(index);
  var shouldBe = board[index[0]][index[1]];
  if (query.length == 0 ){
    if (warn){
      console.log("no jquery found at index", index);
    }
    if (repair){
      query = $(createTileHTML(index[0], index[1], board, false));
      $(tiles).append(query);
    }
  }
  else if (query.length == 1){
    is = query.html()
    if (is != shouldBe){
      if (warn){
        console.log("at index:", index, "is:", is, "should be:", shouldBe);
      }
      if (repair){
        query.html(shouldBe);
      }
    }
  } else {
    console.log("HUSTON, WE HAVE A PROBLEM!!!");
  }
}

function duplicates(repair, warn){
  
}

function _stateAtJQuery(jQuery, board, repair, warn){
  var is = jQuery.html();
  var id = jQuery.attr("id");
  console.log(jQuery.attr("id"));
  /*if (id == "undefined"){
    jQuery.remove();
  }*/
  var index = extractRowCol();
  var shouldBe = board[index[0]][index[1]];
  if( is != shouldBe ){
    if (warn){
      console.log("at index:", index, "is:", jQuery.html(), "should be:", shouldBe);
    }
    if (repair){
      jQuery.html(shouldBe);
    }
  }
}
  
//TODO -- not to do, broken, refactor
function repairState(board){
  repairJQuery = stateAtJQuery(true, true);
  repairAtIndex = stateAtIndex(true, true);
  $(tiles).children().each(function(_, child){
    //console.log(child.getID());
    repairJQuery($(child), board);
  });
  for(var i = 0; i < boardSize; i++){
    for(var ii = 0; ii < boardSize; ii++){
      if(board[i][ii] != 0){
        repairAtIndex([i, ii], board);
      }
    }
  }

  /*var children = $(tiles).children();
  if (expectedNumber == children.length){
    $.each(children, function(_, htmlchild){
      var jqchild = $(htmlchild);
      var rowCol = extractRowCol(htmlchild.id);
      var is = jqchild.html();
      var shouldBe = board[rowCol[0]][rowCol[1]]
      if( is != shouldBe ){
        console.log("rowCol: ", rowCol, "is: ", is, "shouldBe: ", shouldBe);
        jqchild.html(shouldBe);
      }
    });*/
  /*} else {
    console.log("wrong number");
  }*/
}


//------------------------------- MAIN FUNCTIONS -------------------------------
$(document).ready(
  function(){
    //this step is for security/ to prevent clickjacking
    setupCSRF();
    //purely visual, plots nice tile slots aka placeholders
    prepareSlots();
    //getting a 4x4 array from server
    var board = orderBoard();
    //printing the tiles as obtained from the server
    appendTiles(board);
  });


$(document).keydown(function(key){
    var direction = input(key);
    if (direction != null){
      var data = nextMove(direction);
      var newpos = data["newpos"];
      var newboard = data["newboard"];
      var oldboard = data["oldboard"];
      var mergemoves = data["merge_moves"];
      var clearmoves = data["clear_moves"];
      var oldNo = data["oldNo"];
      var newNo = data["newNo"];
      
      //repairState(oldboard);
      //checkState(oldboard, data["oldNo"]);
      //stateAtIndex(true, true)([0, 1], [[0, 8, 2, 3],[3, 5, 7, 9],[12, 13, 14, 15],[21, 22, 23, 24]]);
      //eachSlot(function(index, jquery, _){console.log(jquery)}, "hlep");
      eachMove(clearmoves, preRename);
      eachMove(clearmoves, moveTile(newboard));
      eachMove(mergemoves, moveTile(newboard));
      eachMove(mergemoves, removeTile);
      if (newpos != null){
        appendTile(newpos[0], newpos[1], newboard);
      }
      postRenameAll();
      //checkState(newboard, newNo);
    }
    
});


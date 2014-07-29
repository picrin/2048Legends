//Copyright (c) Adam Kurkiewicz 2014, all rights reserved.

//Please mind that currently any derivative work or unauthorized use is
//prohibited. This code is expected to be released under permissive licence
//after the competition. Currently it is shared for review purpose only.


//------------------------------ GLOBAL CONSTANTS ------------------------------
var boardSize = 4;
var gapSize = 10; //currently in pxs, might migrate to something more reasonable
var tileSize = 80 + gapSize; // vide supra
var quick = 160; //ms

//We will keep jquery with references to DOM elements representing tiles in a
//4x4 array.
var DOMBoard = createBoard();

//the divs we'll be appending to and removing from.
//id of the div to keep tiles in, most of work will be done on this div.
var tiles = "#tiles";
//id of the div to keep slots in, i.e. squares which remain a static background 
var slots = "#tile-placeholders";


//--------------------------------- TEMPLATES ---------------------------------
//A few Mustache templates follow, gutted there's just no better place to keep
//them (a separate file would be ideal)

//Template for tiles
var tile_template ='\
<div class="tile" style="left: {{leftpx}}px; top: {{toppx}}px;">\
  {{value}}\
</div>\
';

//Template for slots
var slot_template = '\
<div class="tile-placeholder" style="left: {{leftpx}}px; top: {{toppx}}px;">\
</div>\
';

//wee template for pxs.
var valuepx = "{{value}}px";


//---------------------- BOARD CREATION AND MANIPULATION ----------------------

function createBoard(){
  board = [];
  for(var i = 0; i < boardSize; i++){
    board.push([]);
  }
  $.each(board, function(_, subarray){
    for(var ii = 0; ii < boardSize; ii++){
      subarray.push(null);
    }
  });
  return board;
}

function _copyBoardAt(oldBoard, newBoard, index, newIndex){
  newBoard[newIndex[0]][newIndex[1]] = oldBoard[index[0]][index[1]];
}

function boardCopier(oldBoard, newBoard){
  return function(from, to){
    _copyBoardAt(oldBoard, newBoard, from, to);
  }
}


//------------------------------ HELPER FUNCTIONS ------------------------------
//this computes a relative coordinate in units (px, but I might migrate to
//something more relative).
function coordinate(index){
  return tileSize * index + gapSize;
}

//this is a pure function. Creates HTML nicely styled with css, which can be
//furhter worked on or appended to the appropriate div. Notice how the
//properties left and top are in fact treated as variables, as they keep state.
function createTileHTML(rowNo, colNo, value){
  var values = {
    value: value,
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

function eachStatic(staticMoves, func){
  $.each(staticMoves, function(_, tuple){
    func(tuple, tuple);
  });
}


//------------------------------ DOM MANIPULATION ------------------------------
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
  //loop through rows
  for (var i = 0; i < boardSize; i++){
    //loop through columns, 
    for (var ii = 0; ii < boardSize; ii++){
      if (board[i][ii] != 0){
        appendTile(i, ii, board[i][ii]);
      }
    }
  }
}

function appendTile(x, y, value){
  var tile = $(createTileHTML(x, y, value));
  $(tiles).append(tile);
  DOMBoard[x][y] = tile;
  return tile
}

function ifDetach(jq, bool){
  if(bool){
    return function(){
      jq.detach();
    }
  } else{
    return undefined
  }
}

function detachAll(){
  for(var i; i < boardSize; i++){
    for(var ii; ii < boardSize; ii++){
      var tile = DOMBoard[i][ii];
      if (tile !== null){
        tile.detach();
      }
    }
  }
}


//--------------------------------- ANIMATIONS ---------------------------------

function animateAppear(jq){
  jq.hide();
  return setTimeout(function(){jq.show()}, quick);
}

function updateHTML(_, index){
  var tile = DOMBoard[index[0]][index[1]];
  var value = tile.html();
  return setTimeout(function(){tile.html(value * 2)}, quick);
}

function animate(board, remove){
  for(var i = 0; i < boardSize; i++){
    for(var ii = 0; ii < boardSize; ii++){
      var tile = board[i][ii];
      if (tile !== null){
        var leftpx = Mustache.render(valuepx, {value: coordinate(i)});
        var toppx = Mustache.render(valuepx, {value: coordinate(ii)});
        tile.animate({top: leftpx, left: toppx}, quick, ifDetach(tile, remove));
      }
    }
  }
}


//----------------------- NETWORK/ KEYBOARD IO FUNCTIONS -----------------------

function nextMove(directioncode, url){
  var board_data = null;
  $.ajax({
    type: 'POST',
    url: url,
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

//------------------------------- MAIN FUNCTIONS -------------------------------
$(document).ready(
  function(){
    //this step is for security/ to prevent clickjacking
    setupCSRF();
    //purely visual, plots nice tile slots aka placeholders
    prepareSlots();
    //getting a 4x4 array from server
    board = orderBoard();
    //printing the tiles as obtained from the server
    //appendTile(0, 1, 23);
    //console.log(copyBoard(board));
    //console.log(board);
    appendTiles(board);
    
  });


$(document).keydown(function(key){
  var direction = input(key);
  if (direction != null){ 
    //data from request
    var data = nextMove(direction, 'nextmove');
    //console.log(data);
    
    var newpos = data["newpos"];
    var oldBoard = data["oldboard"];
    
    detachAll();
    appendTiles(oldBoard);
    
    var mergeMoves = data["merge_moves"];
    var clearMoves = data["clear_moves"];
    var staticMoves = data["static_moves"];
    
    var newPersistBoard = createBoard();
    var newTempBoard = createBoard();
    
    copierPersist = boardCopier(DOMBoard, newPersistBoard);
    copierTemp = boardCopier(DOMBoard, newTempBoard);
    eachStatic(staticMoves, copierPersist);
    eachMove(clearMoves, copierPersist);
    DOMBoard = newPersistBoard;
    if (newpos != null){
      animateAppear(appendTile(newpos[0], newpos[1], 2));
    }

    eachMove(mergeMoves, copierTemp);
    eachMove(mergeMoves, updateHTML);

    animate(newTempBoard, true);
    animate(newPersistBoard, false);

  }
});


//Copyright (c) Adam Kurkiewicz 2014, all rights reserved.

//Please mind that currently any derivative work or unauthorized use is
//prohibited. This code is expected to be released under permissive licence
//after the competition. Currently it is shared for review purpose only.

//-------------------------------- 2048wc.com --------------------------------

//don't worry about polluting the namspace -- there are more valid 45-character
//javascript identifiers than atoms in the universe:
//www.wolframalpha.com/input/?i=53+*+64%5E44+%2F+%28number+of+atoms+in+the+universe%29
window.xVJ0NVCaH9voS9bYeRjwha4dLUKEf8f16hmb3ipzAk8XB=function(n){ //n for namespace
  
  //-------------------------------- VARIABLES --------------------------------
  
  //Keeps a jquery with references to DOM elements representing tiles in a
  //4x4 array.
  n.DOMBoard;
  
  //-------------------------------- CONSTANTS --------------------------------
  
  n.boardSize = 4;
  n.tileToGapRatio = 8; // The ratio of one tile to one gap between two tiles.
  n.quick = 160; //ms
  n.unitsNo = (n.tileToGapRatio + 1) * n.boardSize + 1
  
  //the divs we'll be appending to, working with and removing from.
  //id of the div to keep tiles in, most of work will be done on n div.
  n.tiles = "#tiles";
  //id of the div to keep slots in, i.e. squares which remain a static background 
  n.slots = "#tile-placeholders";
  n.gameboard = "#gameboard";
  
  
  //-------------------------------- TEMPLATES --------------------------------
  //A few Mustache templates follow, gutted there's just no better place to keep
  //them. A separate file would be ideal, but javascript :`( 
  
  //Template for tiles
  n.tile_template ='\
  <div class="tile" style="left: {{leftpx}}px; top: {{toppx}}px; width: {{widthpx}}px; height: {{heightpx}}px">\
    {{value}}\
  </div>\
  ';
  
  //Template for slots
  n.slot_template = '\
  <div class="tile-placeholder" style="left: {{leftpx}}px; top: {{toppx}}px; width: {{widthpx}}px; height: {{heightpx}}px">\
  </div>\
  ';
  
  //wee template for pxs.
  n.valuepx = "{{value}}px";
  
  
  //--------------------- BOARD CREATION AND MANIPULATION ---------------------
  
  //pure function to create an empty 4x4 array.
  n.createBoard = function(){
    var board = [];
    for(var i = 0; i < n.boardSize; i++){
      board.push([]);
    }
    $.each(board, function(_, subarray){
      for(var ii = 0; ii < n.boardSize; ii++){
        subarray.push(null);
      }
    });
    return board;
  };
  
  n._copyBoardAt = function(oldBoard, newBoard, index, newIndex){
    newBoard[newIndex[0]][newIndex[1]] = oldBoard[index[0]][index[1]];
  };
  
  //curried function to copy an element between two NxN arrays. oldBoard is a
  //source array, newBoard is a destination array, from is source index, to is 
  //destination index.
  n.boardCopier = function(oldBoard, newBoard){
    return function(from, to){
      n._copyBoardAt(oldBoard, newBoard, from, to);
    };
  };
  
  
  //----------------------------- HELPER FUNCTIONS -----------------------------
  
  //this returns current width of gameboard
  n.width = function(){
    return $(n.gameboard).width();
  };
  
  //this computes the size of one unit -- aka space in pxs between 2 nearest tiles.
  n.unitSize = function(){
    return n.width()/n.unitsNo;
  };
  
  //this computes a relative coordinate in pxs.
  n.coordinate = function(index){
    return n.unitSize() * ((n.tileToGapRatio + 1) * index + 1);
  };
  
  //this computes the size of the tile.
  n.tileSize = function(){
    return n.unitSize()*n.tileToGapRatio;
  };
  
  //this is a pure function. Creates HTML nicely styled with css, which can be
  //furhter worked on or appended to the appropriate div. Notice how the
  //properties left and top are in fact treated as variables, as they keep state.
  n.createTileHTML = function(rowNo, colNo, value){
    var values = {
      value: value,
      leftpx: n.coordinate(colNo),
      toppx: n.coordinate(rowNo),
      widthpx: n.tileSize(),
      heightpx: n.tileSize(),
      rowNo: rowNo,
      colNo: colNo,
    };
    return window.Mustache.render(n.tile_template, values);
  };
  
  //iterate over every move, and call a func(from, to), where from and to are
  //syntactically arrays of length two, and semantically coordinates.
  n.eachMove = function(moves, func){
    $.each(moves, function(row_i, rows){
      $.each(rows, function(col_i, newpos){
        func([row_i, col_i], newpos);
      });
    });
  };
  
  n.eachStatic = function(staticMoves, func){
    $.each(staticMoves, function(_, tuple){
      func(tuple, tuple);
    });
  };
  
  
  //----------------------------- DOM MANIPULATION -----------------------------
  //These two functions modify appropriate DOM elements adding html and css
  //to make a game board from it (with slots and tiles and shit).
  
  n.prepareSlots = function(){
    $(n.slots).empty();
    for (var i = 0; i < n.boardSize; i++){
      for (var ii = 0; ii < n.boardSize; ii++){
          var values = {
            leftpx: n.coordinate(i),
            toppx: n.coordinate(ii),
            widthpx: n.tileSize(),
            heightpx: n.tileSize()
          };
          var slot_html = window.Mustache.render(n.slot_template, values);
          $(n.slots).append(slot_html);
      }
    }
  };
  
  n.appendTiles = function(board){
    $(n.tiles).empty();
    //loop through rows
    for (var i = 0; i < n.boardSize; i++){
      //loop through columns, 
      for (var ii = 0; ii < n.boardSize; ii++){
        if (board[i][ii] !== 0){
          n.appendTile(i, ii, board[i][ii]);
        }
      }
    }
  };
  
  n.appendTile = function(x, y, value){
    var tile = $(n.createTileHTML(x, y, value));
    $(n.tiles).append(tile);
    n.DOMBoard[x][y] = tile;
    return tile;
  };
  
  n.ifDetach = function(jq, bool){
    if(bool){
      return function(){
        jq.detach();
      };
    } else{
      return undefined;
    }
  };
  
  
  //-------------------------------- ANIMATIONS --------------------------------
  
  n.animateAppear = function(jq){
    jq.hide();
    return setTimeout(function(){jq.show()}, n.quick);
  };
  
  n.updateHTML = function(_, index){
    var tile = n.DOMBoard[index[0]][index[1]];
    var value = tile.html();
    return setTimeout(function(){tile.html(value * 2)}, n.quick);
  };
  
  n.animate = function(board, remove){
    for(var i = 0; i < n.boardSize; i++){
      for(var ii = 0; ii < n.boardSize; ii++){
        var tile = board[i][ii];
        if (tile !== null){
          var leftpx = window.Mustache.render(n.valuepx, {value: n.coordinate(i)});
          var toppx = window.Mustache.render(n.valuepx, {value: n.coordinate(ii)});
          tile.animate({top: leftpx, left: toppx}, n.quick, n.ifDetach(tile, remove));
        }
      }
    }
  };
  
  n.resizeTiles = function(){
    for(var i = 0; i < n.boardSize; i++){
      for(var ii = 0; ii < n.boardSize; ii++){
        var tile = n.DOMBoard[i][ii];
        if (tile !== null){
          tile.css("left", n.coordinate(ii) + "px");
          tile.css("top", n.coordinate(i) + "px");
          tile.css("height", n.tileSize() + "px");
          tile.css("width", n.tileSize() + "px");
        }
      }
    }
  };
  
  
  //---------------------- NETWORK/ KEYBOARD IO FUNCTIONS ----------------------
  
  n.negotiateMove = function(direction, clientSecret, clientCommitment){
    //these variables are here to keep state for eventual 
    var serverCommitment;
    var allempty;
    
    //Client commits to a random number by sending a hex-encoded sha256 of
    //that number. Server in turn commits to its number choice. 
    var commit = function(){
      $.ajax({
        type: 'POST',
        url: 'exchangeCommitments',
        data: {clientSecretHashed : clientCommitment,
               direction: direction},
        async: false,
        statusCode:{
          200: processServerCommitment,
          452: reveal(true)
        }
      });
    };
    
    var processServerCommitment = function(data){
      var oldBoard = data["oldboard"];
      
      $(n.tiles).empty();
      n.appendTiles(oldBoard);
        
      var mergeMoves = data["merge_moves"];
      var clearMoves = data["clear_moves"];
      var staticMoves = data["static_moves"];
        
      var newPersistBoard = n.createBoard();
      var newTempBoard = n.createBoard();
      
      var copierPersist = n.boardCopier(n.DOMBoard, newPersistBoard);
      var copierTemp = n.boardCopier(n.DOMBoard, newTempBoard);
      
      n.eachStatic(staticMoves, copierPersist);
      n.eachMove(clearMoves, copierPersist);
      
      n.DOMBoard = newPersistBoard;
      
      n.eachMove(mergeMoves, copierTemp);
      n.eachMove(mergeMoves, n.updateHTML);
      
      n.animate(newTempBoard, true);
      n.animate(newPersistBoard, false);
      //TODO use some sort of reactive programming or monad to get rid of it.
      serverCommitment = data["serverSecretHashed"];
      console.log(serverCommitment);
      allempty = data["allempty"];
      reveal(false)();
    };
    
    var reveal = function(surrender){
      var request = {
        type: 'POST',
        url: "exchangeSecrets",
        data: {
          surrender: surrender,
          clientSecret: clientSecret
        },
        async: true,
        statusCode:{
          200: processServerSecret,
          452: function(_){console.error("out of order secret exchange request")}
        }
      };
      
      if (surrender === true){
        request.data.clientSecret = "X";
      }
      return function(secret){
        $.ajax(request);
      };
    };
    
    var processServerSecret = function(data){
      var serverSecret = data["serverSecret"];
      var expectedServerCommitment = window.CryptoJS.SHA256(serverSecret).toString();
      //TODO check and blame if correct all_empty.
      if (expectedServerCommitment !== serverCommitment){
        console.error("server Cheating");
        console.error("expected:", expectedServerCommitment);
        console.error("received:", serverCommitment);
      }
      //var serverSecretHashedNumber = ;
      //varnum = serverSecretNumber.toString(16)
      var xoredHex = [];
      var len = serverSecret.length;
      for(var i = 0; i < len; i++){
        xoredHex[i] = (parseInt(serverSecret[i], 16) ^
                       parseInt(clientSecret[i], 16)
                       ).toString(16);
      }
      xoredHex = xoredHex.join("");
      var serverXoredHex = data["randomNumber"];
      //TODO check soundness
      //if (newpos !== null){
      //  n.animateAppear(n.appendTile(newpos[0], newpos[1], 2));
      //}
      //console.log("xored", xoredHex.join(""));
      //console.log("sored", serverXoredHex);
      n.checkAndBlame(xoredHex, serverXoredHex);
      var position = window.BigNumber(xoredHex, 16);
      position = allempty[position.mod(allempty.length).toNumber()];
      n.checkAndBlame(position[0], data["position"][0]);
      n.checkAndBlame(position[1], data["position"][1]);
      //TODO there's a clever trick to be performed: use undefined instead of nulls (in case of a real empty space), and make nulls denote "real" empty spaces. Then everything should essentialy work, even if one moves the keys really quickly.
      if(n.DOMBoard[position[0]][position[1]] === null){
        n.appendTile(position[0], position[1], data["value"]);
      }
    };
    commit();
  } /* negotiateMove */;
  n.checkAndBlame = function(expected, received){
    if(expected !== received){
      console.error("server Cheating!");
      console.error("expected:", expected);
      console.error("received:", received);
      n.expected = expected;
      n.received = received;
    }
  };
  //Getting a 4x4 array from the server
  n.orderBoard = function(){
    $.ajax({
      type: 'GET',
      url: 'get_board',
      async: true,
      success: n.prepareGame,
    });
  };
  
  //Copy-paste from SO, I do not own the copyright
  n.input = function(key){
      var direction = null;
      switch(key.which){
        case 37: // left
          direction = "left";
        break;
        case 38: // up
          direction = "up";
        break;
        case 39: // right
          direction = "right";
        break;
        case 40: // down
          direction = "down";
        break;
      }
      if (direction !== null){
        key.preventDefault(); // prevent the default action (scroll / move caret)
      }
      return direction;
  };
  
  
  //------------------------------ MAIN FUNCTIONS ------------------------------
  
  n.prepareGame = function(data){
    n.DOMBoard = n.createBoard();
    //purely visual, plots nice tile slots aka placeholders
    n.prepareSlots();
    //printing the tiles as obtained from the server
    n.appendTiles(data["board"]);
    n.onResize();
  };
  
  n.onResize = function() {
    var gameboard = $("#gameboard");
    var gameboardWidth = gameboard.width();
    gameboard.css({'height': gameboardWidth + 'px'});
    n.prepareSlots();
    n.resizeTiles();
  };
  //return object with methods attached.
  return n;
};
if (window.Play2048wc === undefined){
  window.Play2048wc = window.xVJ0NVCaH9voS9bYeRjwha4dLUKEf8f16hmb3ipzAk8XB({});
}
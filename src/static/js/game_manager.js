function GameManager(size, InputManager, Actuator, StorageManager) {
  this.size           = size; // Size of the grid
  this.inputManager   = new InputManager;
  this.storageManager = new StorageManager;
  this.actuator       = new Actuator;
  //this.ajax           = new XMLHttpRequest();

  this.inputManager.on("move", this.move.bind(this));
  this.inputManager.on("restart", this.restart.bind(this));
  this.inputManager.on("keepPlaying", this.keepPlaying.bind(this));
  //this.setup();

  this.grid           = new Grid(this.size);
  this.requestGame();

  this.score       = 0;
  this.game_id = null;
  
}

// Restart the game
GameManager.prototype.restart = function () {
  this.storageManager.clearGameState();
  this.actuator.continueGame(); // Clear the game won/lost message
  //this.setup();
};

// Keep playing after winning (allows going over 2048)
GameManager.prototype.keepPlaying = function () {
  this.keepPlaying = true;
  this.actuator.continueGame(); // Clear the game won/lost message
};

// Set up the initial tiles to start the game with
GameManager.prototype.requestGame = function () {
  var self = this;
  //$.cookie("players_id", "foo", { path: '/' });
  $.get("get_board", {"userid":"1051126"}).done(function(data){
    self.game_id = data["gameid"];
    //console.log(data["board"]);
  
    for (var x in data["board"]) {
      var row = data["board"][x];
      for (var y = 0; y < row.length; y++){
        var value = data["board"][x][y];
        if (value != 0){
          var tile = new Tile({y: parseInt(x), x: y}, value);
          self.grid.insertTile(tile);
          console.log(tile);        
          }
      }
      self.actuator.actuate(self.grid, {})
      //console.log(data["board"][x][y]);
    }
  });
}

// Move a tile and its representation
GameManager.prototype.moveTile = function (tile, cell) {
  this.grid.cells[tile.x][tile.y] = null;
  this.grid.cells[cell.x][cell.y] = tile;
  tile.updatePosition(cell);
};

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = $.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

$.ajaxSetup({
    crossDomain: false, // obviates need for sameOrigin test
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type)) {
	    //console.log("cookie:", getCookie('csrftoken'));
            xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
        }
    }
});

// Move tiles on the grid in the specified direction
GameManager.prototype.move = function (direction) {
  self = this;
$.post("nextmove", { gameid: "12q345908762459876", direction: direction }).done(function(data){
  for (var x in data["moves"]) {
    var ys = data["moves"][x];
    for (var y in ys){
      console.log(data["moves"][x][y], x, y);
      newpos = data["moves"][x][y];
      tile = self.grid.cells[x][y];
      console.log(tile);
      self.moveTile(tile, {y:newpos[0], x:newpos[1]})      
      //self.grid.cells[newpos[0]][newpos[1]] = tile;
      //tile.updatePosition({x: newpos[0], y:newpos[1]});
      //self.grid.cells[x][y];
      self.actuator.actuate(self.grid, {});
    }
  }

});
};


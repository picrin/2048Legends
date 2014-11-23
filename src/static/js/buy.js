
function getPriceForGames(numberOfGames) {
  return pricePerGame * numberOfGames;
}

function buyButtonCallback(response) {
  alert(response);
}

$("#buybutton").click(function(c){
  var numberOfGames = parseInt($("#buybutton").value);
  
  var priceForGames = getPriceForGames(numberOfGames);
  alert("YO YO YO"+priceForGames);
  
  $.get(
    '/buybuttonclick',
    {'intended_plays':numberOfGames, 'intended_currency':priceForGames},//empty parameters
    buyButtonCallback                   
   );  
  
});
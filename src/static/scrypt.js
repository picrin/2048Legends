//Copyright (c) Adam Kurkiewicz 2014, all rights reserved.

// variable shared_secret is shared between Ula (user) an Sergiey (Server), but
// should be kept secret from Eve (eavesdroppers). This can be achieved by
// https. Ula needs to keep variable "secretSeed" secret from everybody,
// particuarly from Sergiey. If Sergiey gets to know Ula's secretSeed, he can
// predict her random numbers, and cheat during random number negotiation.


var salt = "Nic dwa razy sie nie zdarza i nie zdarzy. Z tej przyczyny zrodzilismy sie bez wprawy i pomrzemy bez rutyny."
var N = 16384
var r = 8
var p = 1
var scrypt = scrypt_module_factory()

function stretch_key(key, salt, N, r, p){
	var hash = scrypt.crypto_scrypt(
	  scrypt.encode_utf8(key),
	  scrypt.encode_utf8(salt),
	  N, r, p, 32
	)
	return scrypt.to_hex(hash)
}

function stretch_password(user, password) {
  var combUsrPass = CryptoJS.HmacSHA256(user,password).toString()
  return stretch_key(combUsrPass, salt, N, r, p)
}
function nextRandom(){
  var nextRandomStore = CryptoJS.HmacSHA256(
      localStorage.getItem("secretSeed"),
      localStorage.getItem("nextRandom")
  ).toString()
  localStorage.setItem("nextRandom", nextRandomStore)
  return new BigNumber(nextRandomStore, 16)
}
$(document).ready(
  function(){
    //this step is for security/ to prevent clickjacking
    setupCSRF();
  });
  
function negotiateRandomNumber(){
  var clientSecretNumber = nextRandom()
  var clientSecret = clientSecretNumber.toString(16)
  var clientSecretHashed = CryptoJS.SHA256(clientSecret).toString()
  var serverSecretHashed = null
  var serverSecret = null
  var serverSecretNumber = null
  
  function firstStep(data){
    $.ajax({
      type: 'POST',
      url: "negotiate_first",
      data: {clientSecretHashed: clientSecretHashed},
      async: true,
      success: secondStep
    });
  }
  
  function secondStep(data){
    serverSecretHashed = data["serverSecretHashed"]
    $.ajax({
      type: 'POST',
      url: "negotiate_second",
      console.log(clientSecret)
      data: {clientSecret: clientSecret, serverSecretHashed: serverSecretHashed},
      async: true,
      success: thirdStep
    });
  }
  
  function thirdStep(data){
    serverSecret = data["serverSecret"]

    //set appropriate secret in the variables above.
  }
  
  firstStep()
}

$("#negotiate").click(function(){
  negotiateRandomNumber()
});


$("#submit").click(function(){
  var username = $("#username").val()
  var password = $("#password").val()
  var preSecret = stretch_password(username, password)
  var sharedSecret = CryptoJS.SHA256(preSecret).toString()
  var secretSeed = CryptoJS.HmacSHA256(preSecret, Date.now().toString()).toString()
  localStorage.setItem("secretSeed", secretSeed)
  localStorage.setItem("nextRandom", CryptoJS.SHA256("").toString())
  $.ajax({
    type: 'POST',
    url: "signin",
    data: {username: username, password: sharedSecret},
    async: false,
    success: function(_){}
  });
  //console.log(localStorage.getItem("nextRandom"))
  for(var i = 0; i < 10; i++){
    console.log(nextRandom().modulo(1000).toNumber())
  }
  //console.log(CryptoJS.SHA256("gugugu")["words"][0])
  //console.log("secretSeed:" + secretSeed)
});


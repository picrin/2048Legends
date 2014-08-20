//Copyright (c) Adam Kurkiewicz 2014, all rights reserved.

// variable shared_secret is shared between Ula (user) an Sergiey (Server), but
// should be kept secret from Eve (eavesdroppers). This can be achieved by
// https. Ula needs to keep variable "secretSeed" secret from everybody,
// particuarly from Sergiey. If Sergiey gets to know Ula's secretSeed, he can
// predict her random numbers, and cheat during random number negotiation.

window.tZKN5DLe6lyf8Fjx8gb3AKqb8gXkxd7EqMTnAV3Vj26RL = function(n){ 
  n.scrypt = window.scrypt_module_factory();
  n.salt = "2048wc.com says: Nic dwa razy sie nie zdarza i nie zdarzy. Z tej przyczyny zrodzilismy sie bez wprawy i pomrzemy bez rutyny.";
  n.N = 16384;//WARNING -- this value of N parameter will crash firefox with DEV-TOOLS open. It won't crash it without dev-tools.
  //n.N = 2048; If evidence is presented that number above is too large, use a uncomment this.
  n.r = 8;
  n.p = 1;
  
  n.nextRandom = function(){
    var array = new Uint32Array(8);
    window.crypto.getRandomValues(array);

    var hexString = "";
    var hex;
    for (var i = 0; i < array.length; i++) {
      hex = array[i].toString(16);
      hex = (Math.pow(10, (8 - hex.length)) + "").substring(1, 9) + hex;
      hexString += hex; 
    }
    return hexString;
  };

  n.randomWithHash = function(){
    var random = n.nextRandom();
    return {
      random: random,
      randomHash: window.CryptoJS.SHA256(random).toString()
    };
  };
  
  n.stretch_key = function(key, salt, N, r, p){
  	var hash = n.scrypt.crypto_scrypt(
  	  n.scrypt.encode_utf8(key),
  	  n.scrypt.encode_utf8(salt),
  	  N, r, p, 32
  	);
  	return n.scrypt.to_hex(hash);
  };
  
  n.stretch_password = function(user, password) {
    var combUsrPass = window.CryptoJS.HmacSHA256(user,password).toString();
    return n.stretch_key(combUsrPass, n.salt, n.N, n.r, n.p);
  };
  
  n.nextRandomLegacy = function(){
    var nextRandomStore = window.CryptoJS.HmacSHA256(
        localStorage.getItem("secretSeed"),
        localStorage.getItem("nextRandom")
    ).toString();
    localStorage.setItem("nextRandom", nextRandomStore);
    return new window.BigNumber(nextRandomStore, 16);
  };
  
  n.negotiateRandomNumber = function(){
    var clientSecretNumber = n.nextRandom();
    var clientSecret = clientSecretNumber.toString(16);
    var clientSecretHashed = window.CryptoJS.SHA256(clientSecret).toString();
    var serverSecretHashed = null;
    var serverSecret = null;
    var serverSecretNumber = null;
    
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
      serverSecretHashed = data["serverSecretHashed"];
      $.ajax({
        type: 'POST',
        url: "negotiate_second",
        data: {clientSecret: clientSecret, serverSecretHashed: serverSecretHashed},
        async: true,
        success: thirdStep
      });
    }
    
    function thirdStep(data){
      serverSecret = data["serverSecret"];
  
      //set appropriate secret in the variables above.
    }
    
    firstStep();
  };
  
  n.negotiateClick = function(){
    n.negotiateRandomNumber();
  };
  
  n.register = function(){
    var username = $("#username").val();
    var password = $("#password").val();
    var preSecret = n.stretch_password(username, password);
    var sharedSecret = window.CryptoJS.SHA256(preSecret).toString();
    var secretSeed = window.CryptoJS.HmacSHA256(preSecret, Date.now().toString()).toString();
    localStorage.setItem("secretSeed", secretSeed);
    localStorage.setItem("nextRandom", window.CryptoJS.SHA256("").toString());
    $.ajax({
      type: 'POST',
      url: "signup",
      data: {username: username, password: sharedSecret},
      async: true,
      success: function(_){}
    });
  };
  
  n.submitClick = function(){
    var username = $("#username").val();
    var password = $("#password").val();
    var preSecret = n.stretch_password(username, password);
    var sharedSecret = window.CryptoJS.SHA256(preSecret).toString();
    var secretSeed = window.CryptoJS.HmacSHA256(preSecret, Date.now().toString()).toString();
    localStorage.setItem("secretSeed", secretSeed);
    localStorage.setItem("nextRandom", window.CryptoJS.SHA256("").toString());
    $.ajax({
      type: 'POST',
      url: "signin",
      data: {username: username, password: sharedSecret},
      async: true,
      success: function(_){location.replace("/")}
    });
    //console.log(localStorage.getItem("nextRandom"))
    //console.log(CryptoJS.SHA256("gugugu")["words"][0])
    //console.log("secretSeed:" + secretSeed)
  };
  return n;
};
if (window.Crypto2048wc === undefined){
  window.Crypto2048wc = window.tZKN5DLe6lyf8Fjx8gb3AKqb8gXkxd7EqMTnAV3Vj26RL({});
}
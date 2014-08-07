// these three methods are a necessary copy-paste to do the CSRF trick.
//I do not own the copyright
window.pwHr0cSAhSH5rQ1ILqv1iUCiSnWR8PTqLA9pWEQ33RShu=function(n){ // n for namespace
  n.getCookie = function(name) {
    var cookieValue = null;
      if (document.cookie && document.cookie !== "") {
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
  };
    
  n.csrfSafeMethod = function(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
  };
    
  n.setupCSRF = function(){
    $.ajaxSetup({
      crossDomain: false,
      beforeSend: function(xhr, settings) {
        if (!n.csrfSafeMethod(settings.type)) {
          xhr.setRequestHeader("X-CSRFToken", n.getCookie('csrftoken'));
        }
      }
    });
  };
  return n;
};
if (window.Csrf2048wc === undefined){
  window.Csrf2048wc = window.pwHr0cSAhSH5rQ1ILqv1iUCiSnWR8PTqLA9pWEQ33RShu({});
}
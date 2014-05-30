// these three methods are a necessary copy-paste to do the CSRF trick.
//I do not own the copyright
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

function setupCSRF(){
  $.ajaxSetup({
      crossDomain: true, // test it, why not!
      beforeSend: function(xhr, settings) {
          if (!csrfSafeMethod(settings.type)) {
             xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
          }
      }
  });
}

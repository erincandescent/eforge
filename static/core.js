var RecaptchaOptions = {
  'theme': 'white',
};

$(document).ready(function() {
    $("button, input:submit, .button").button()
    $(".highlight").addClass("ui-state-highlight ui-corner-all")
    $(".error").addClass("ui-state-error ui-corner-all");
    $("#message-dismiss").click(function() { $("#messages").slideUp(); });
});

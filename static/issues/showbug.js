$(function() {
    $("#bug-tabs").tabs();
    $("#bug-tabs h3").hide();
    $(".bug-clink").click(function() {
        $('#bug-tabs').tabs('select', 'bug-comments');
        return true;
    });

    $("#id_bug-status").change(statusUpdate);
    statusUpdate();
});

function statusUpdate() {
    var resolved = ($("#id_bug-status").val() == 5);


    if(!resolved) {
        $("#id_bug-resolution").attr("disabled","disabled");
    } else {
        $("#id_bug-resolution").removeAttr("disabled");
    }
}


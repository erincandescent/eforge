$(function() {
    $("#manage-tabs").tabs({
        load: function(event, ui) {
            restylePanel(ui);
        }
    });
});

function restylePanel(ui) {
    $("a", ui.panel).click(function() {
            $(ui.panel).load(this.href, function() {
                restylePanel(ui);
            });
            return false;
        });

    $("form", ui.panel).ajaxForm({
        success: function(responseText) {
            $(ui.panel).html(responseText);
            restylePanel(ui);
            return false;
        },
    });
}
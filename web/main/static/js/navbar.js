$(document).ready(function() {

    let drop_down_menu = $("#dropdown-menu");

    drop_down_menu.click(function () {
        let element = $("#nav-drop-down");
        if (element.hasClass("show")){
            element.removeClass("show")
        }else{
            element.addClass("show");
        }
    });

});
// Quotes Page

$(document).on("submit",".like", function(e){
    e.preventDefault();
    $.ajax({
        url: "quotes/like",
        type: "POST",
        data: $(this).serialize(),
        success: function(serverResponse){
            $("#quotes").html(serverResponse);
        }
    })
})

$(document).on("submit",".unlike", function(e){
    e.preventDefault();
    $.ajax({
        url: "quotes/unlike",
        type: "POST",
        data: $(this).serialize(),
        success: function(serverResponse){
            $("#quotes").html(serverResponse);
        }
    })
})

// Account Page

$(document).on("submit",".unlike_account", function(e){
    e.preventDefault();
    $.ajax({
        url: "quotes/unlike",
        type: "POST",
        data: $(this).serialize(),
        success: function(serverResponse){
            $("#quotes").html(serverResponse);
        }
    })
})
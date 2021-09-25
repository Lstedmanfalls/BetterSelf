$(document).on("submit",".like", function(e){
    e.preventDefault();
    $.ajax({
        url: "quotes/like",
        type: "POST",
        data: 
            $(this).serialize(),
        success: function(){
            console.log("it worked")
        }
    })
})

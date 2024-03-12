(function () {
    var fieldBlock = $('#field');
    var gameInfo = fieldBlock[0].dataset;
    field = new TicTacField(gameInfo.size, gameInfo.min_length);


    fieldBlock.html(field.render());

    var jqxhr = $.ajax({
        url: gameInfo.history_url
    });
    jqxhr.done(function (data) {
        console.log(data);
        var timeout = 0;
        for(var i=0; i<data.moves.length; i++){
            setTimeout((function () {
                field.setCellValue(data.moves[this].x, data.moves[this].y, ['X', 'O'][this%2]);
            }).bind(i), timeout);
            timeout += 500;
        }
        setTimeout(function(){
            field.highlightLine(data.finish_line, "#18c155")
        }, timeout);
    });
    jqxhr.fail(function(data){
        alert('An error occured');
        console.log(data);
    });

})();


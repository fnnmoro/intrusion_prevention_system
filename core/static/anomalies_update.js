$(document).ready(function(){
    //connect to the socket server.
    var socket = io.connect('http://' + document.domain + ':' + location.port + '/test');

    //receive details from server
    socket.on('mytest', function(msg) {
        if (msg["total_anomalies"] > 0){
            $('#num_anomalies').html(msg["total_anomalies"]).css("color", "red");
        }

        $('#num_anomalies').click( function() {
            alert('blacklist');
        });
    });

});
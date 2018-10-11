$(document).ready(function(){
    //connect to the socket server.
    var socket = io.connect('http://' + document.domain + ':' + location.port + '/test');

    //receive details from server
    socket.on('mytest', function(msg) {
        $('#num_anomalies').html(msg["total_anomalies"]);

        $('#num_anomalies').click( function() {
            alert('blacklist');
        });
    });

});
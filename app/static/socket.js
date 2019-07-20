$(document).ready(function changeColor() {
    // connect to the server
    var socket = io.connect('http://' + document.domain + ':' + location.port + '/detection');

    // receive details from server
    socket.on('realtime', function(msg) {
        if (msg['anomalous_flows'] > 0){
            $('#anomalies').html(msg['anomalous_flows']).css('color', 'red');
        }
    });
});

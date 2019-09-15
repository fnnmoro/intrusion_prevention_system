$(document).ready(function() {
    num_intrusions = $('#intrusions').text();    
    if (num_intrusions > 0){
        $('#intrusions').html(num_intrusions).css('color', 'red');
    }

    // connect to the server
    var socket = io.connect('http://' + document.domain + ':' + location.port + '/realtime');

    // receive details from server
    socket.on('detection', function(msg) {
        if (msg['num_intrusions'] > 0){
            $('#intrusions').html(msg['num_intrusions']).css('color', 'red');
        }
    });
});

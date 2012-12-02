var PUSHER_KEY = "71880b602ec7534b0b4f";

DP.RealTime = function() {
    this.setup();
};

DP.RealTime.prototype = {
    
    setup: function() {
        this.pusher = new Pusher(PUSHER_KEY);
        this.channel = this.pusher.subscribe(DP.Round.url);
    }
    
};


$(document).ready(function() {

    DP.realtime = new DP.RealTime();

});
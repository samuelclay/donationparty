DP.RealTime = function() {
    this.setup();
};

DP.RealTime.prototype = {
    
    setup: function() {
        this.pusher = new Pusher(DP.PUSHER_KEY);
        this.channel = this.pusher.subscribe(DP.Round.url);
        this.channel.bind('new:charge', _.bind(this.new_charge, this));
        console.log(["Subscribing to real-time", this.pusher, this.channel]);
    },
    
    new_charge: function() {
        console.log(["REAL-TIME: New Charge", arguments]);
        this.reload_donations();
    },
    
    reload_donations: function() {
        $.get('/round_status/' + DP.Round.url, {}, function(data) {
            console.log(["Round status", data]);
            $('.DP-donations').html(data.donations_template);
        });
    }
    
};


$(document).ready(function() {

    DP.realtime = new DP.RealTime();

});
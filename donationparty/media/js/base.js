DP.RealTime = function() {
    this.setup();
};

DP.RealTime.prototype = {
    
    setup: function() {
        this.pusher = new Pusher(DP.PUSHER_KEY);
        this.channel = this.pusher.subscribe(DP.Round.url);
        this.channel.bind('new:charge', _.bind(this.newCharge, this));
        console.log(["Subscribing to real-time", this.pusher, this.channel]);
        
        this.secondsLeft = DP.Round.secondsLeft;
        this.reloader = setInterval(_.bind(this.reloadDonations, this), 1000*60);
        this.timer = setInterval(_.bind(this.renderTimer, this), 1000*1);
    },
    
    newCharge: function() {
        console.log(["REAL-TIME: New Charge", arguments]);
        this.reloadDonations();
    },
    
    reloadDonations: function(data) {
        if (!data) {
            $.get('/round_status/' + DP.Round.url, {}, this.renderDonations);
        } else {
            this.renderDonations(data);
        }
    },
    
    renderDonations: function(data) {
        console.log(["Round status", data]);
        $('.donations').html(data.donations_template);
        $('.payment-info').html(data.payment_info_template);
        this.secondsLeft = data.seconds_left;
        if (data.closed) {
            window.location.href = window.location.href;
        }
    },
    
    renderTimer: function() {
        var $timer = $('.timer');
        var minutes = Math.floor(this.secondsLeft / 60);
        var seconds = this.secondsLeft % 60;
        if (seconds <= 9) seconds = "0" + seconds;
        $timer.html(minutes + ":" + seconds + " <span>time left</span>");
        this.secondsLeft -= 1;
    }
    
};


$(document).ready(function() {
    
    if (!DP.Round.closed) {
        DP.realtime = new DP.RealTime();
        DP.paymentform = new DP.PaymentForm();
    }

});
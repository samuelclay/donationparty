DP.RealTime = function() {
    this.setup();
};

DP.RealTime.prototype = {
    
    setup: function() {
        this.pusher = new Pusher(DP.PUSHER_KEY);
        this.channel = this.pusher.subscribe(DP.Round.url);
        this.channel.bind('new:charge', _.bind(this.newCharge, this));
        console.log(["Subscribing to real-time", this.pusher, this.channel]);
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
    }
    
};


$(document).ready(function() {

    DP.realtime = new DP.RealTime();
    DP.paymentform = new DP.PaymentForm();

});
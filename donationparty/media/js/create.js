$(function(){

    // hide original labels and inputs
    $('.charity input[type=radio], .charity span').hide();
    
    // replace with charity images
    $('.charity img').click(function(){
        
        var $radio = $(this).prev('input:radio');
        
        $('.charity').removeClass('checked', false);
        $(this).parents('.charity').addClass('checked');
        
        // uncheck all charities
        $('.charities input[type=radio]').attr('checked', false);
        
        // check charity
        $radio.attr('checked', true);
    });
    
    // select a random charity
    var rand = Math.floor(Math.random()*5);
    $('.charity img').eq(rand).click();
});
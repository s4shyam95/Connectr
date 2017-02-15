/**
 * Created by s4shyam95 on 15/02/17.
 */
// Add the script to injecthtml here
var mainStyle = '<link href="https://peaceful-hollows-95315.herokuapp.com/static/css/extra.css" rel="stylesheet">'
var addStyle = "<style> #rocketapp-widget .rocketapp-widget-messages>div {margin-left: 0px;}#rocketapp-widget .rocketapp-widget-messages{margin-bottom: 10px;padding: 20px;}#rocketapp-widget .rocketapp-widget-input-container{bottom: 0 !important;}</style>";
$('head').append(mainStyle);
$('head').append(addStyle);


var box = '<div id="rocketapp-button" class="rocketapp-button-float rocketapp-animatable"><div class="rocketapp-button-title">We&#39;re&nbsp;offline.&nbsp;Leave&nbsp;a&nbsp;message.</div><img class="rocketapp-button-icon" src="https://linked.chat:443/static/widget/icons/logo.svg" alt="rocketapp-logo"><img class="rocketapp-button-icon-close" src="https://linked.chat:443/static/widget/icons/close.svg" alt="Minimize chat" title="Minimize chat"></div><div id="rocketapp-widget" class="rocketapp-button-float rocketapp-animatable"><div class="rocketapp-widget-title">Support</div><img class="rocketapp-widget-settings-btn" src="https://linked.chat:443/static/widget/icons/settings.svg" alt="Open settings" title="Open settings"><div class="rocketapp-widget-settings-container"><form><div><input class="rocketapp-widget-input rocketapp-widget-input-login-name" name="name" type="text" placeholder="Name" aria-label="Name" value="paren"></div><div><input class="rocketapp-widget-input rocketapp-widget-input-login-email" name="email" type="text" placeholder="Email" aria-label="Email" value="paren1994@yahoo.com.au"></div><div><input class="rocketapp-widget-login-btn" type="button" value="Save"></div></form></div><img class="rocketapp-widget-close-btn" src="https://linked.chat:443/static/widget/icons/minimize.svg" alt="Minimize chat" title="Minimize chat"><div class="rocketapp-widget-content"><div class="rocketapp-widget-messages"></div><div class="rocketapp-widget-input-container"><form><div><input class="rocketapp-widget-input rocketapp-widget-input-name" name="name" type="text" placeholder="Name" aria-label="Name" value="paren" style="display: none;"></div><div><input class="rocketapp-widget-input rocketapp-widget-input-email" name="email" type="text" placeholder="Email" aria-label="Email" value="paren1994@yahoo.com.au" style="display: none;"></div><div><input class="rocketapp-widget-input rocketapp-widget-input-message" placeholder="Type a message..." aria-label="Type a message..."></div><div><input class="rocketapp-widget-send-btn" type="button" value="Send message" ></div></form></div></div></div>';
$('body').append(box);

var myMessage = '<div class="rocketapp-widget-message-from-visitor"><div></div></div>';
var hisMessage = '<div class="rocketapp-widget-message-from-agent no-agent-name"><div></div></div>';
var messageBox = $('.rocketapp-widget-messages');
var $messages = $(".rocketapp-widget-messages");

var curLen = 0;
var refresh = function() {
    $.ajax({
        method: "GET",
         url: "https://peaceful-hollows-95315.herokuapp.com/get_msgs/",
        data: {
            grp_id: token,
        },
        success: function(result) {
            resetMessages($.parseJSON(result));
        }
    });
    timer = setTimeout(refresh, 5000);

}

var addMessage = function (message, type) {

    if(type==2) {
        var divToAdd = $.parseHTML(myMessage);
    } else {
        var divToAdd = $.parseHTML(hisMessage);
    }
    $(divToAdd).append(message);
    return divToAdd;

}

var resetMessages = function (data) {
    var toAdd = $.parseHTML('<div></div>');
    $.each(data, function(i, item) {
        $(toAdd).append(addMessage(item.mpn.text, item.mpn.by));
    });
    $messages.empty();
    $messages.append($(toAdd).children());
    console.log(data.length);
    if(curLen < data.length) {
        $messages[0].scrollTop = $messages[0].scrollHeight;
        curLen = data.length;
    }

}
var timer;
var token = $("#rocketapp-script").attr("data-attr");

$(document).ready(function () {

    $('.rocketapp-widget-close-btn').click(function() {
        console.log("called");
        $('#rocketapp-widget').removeClass("rocketapp-widget-opened");
        $('#rocketapp-button').removeClass("rocketapp-widget-opened");
    });

    $('.rocketapp-widget-settings-btn').click(function () {
        if($('.rocketapp-widget-settings-container').hasClass('rocketapp-widget-opened')) {
            $('.rocketapp-widget-settings-container').removeClass('rocketapp-widget-opened');
        } else {
            $('.rocketapp-widget-settings-container').addClass('rocketapp-widget-opened')
        }
    });
    $('#rocketapp-button').click(function () {
        if($('#rocketapp-widget').hasClass("rocketapp-widget-opened")) {
            $('#rocketapp-widget').removeClass("rocketapp-widget-opened");
            $('#rocketapp-button').removeClass("rocketapp-widget-opened");
        } else {
            $('#rocketapp-widget').addClass("rocketapp-widget-opened");
            $('#rocketapp-button').addClass("rocketapp-widget-opened");
        }
    });

    $('.rocketapp-widget-input-message').keyup(function(e){
        var code= e.which;
        if(code == 13) $('.rocketapp-widget-send-btn').click();
    });

    $('.rocketapp-widget-send-btn').click(function(e) {
        e.preventDefault();
        if($(".rocketapp-widget-input-message").val()!="" && $(".rocketapp-widget-input-message").val()!=undefined) {
            $.ajax({
                method: "GET",
                url: "https://peaceful-hollows-95315.herokuapp.com/naya_msg/",
                data: {
                    text: $(".rocketapp-widget-input-message").val(),
                    grp_id: token,
                },
                success: function(result) {
                    var divToAdd = addMessage($(".rocketapp-widget-input-message").val(),2);
                    $messages.append(divToAdd);
                    $(".rocketapp-widget-input-message").val("");
                    $messages[0].scrollTop = $messages[0].scrollHeight;
                },
                error: function(result) {
                }
            });
        }
    });
    refresh();

});

sessionStorage.setItem("chatopen", 0);



var closechat = (mode) => {
	mode = mode;
	storeValue('newchat', mode);
}

var store_chatuser = (mode) => {
	mode = mode;
	storeValue('chatuser', mode);
}

var storeValue = (key, value) => {
	if (localStorage) {
		localStorage.setItem(key, value);
	} else {
		$.cookies.set(key, value);
	}
}

var getStoredValue = (key) => {
	if (localStorage) {
		return localStorage.getItem(key);
	} else {
		return $.cookies.get(key);
	}
}


var open_chat_box = () => {
	var mode = getStoredValue('newchat');

	if (mode == null) {
		closechat(1);
		mode = 1;
	}

	if (mode == 1) {
		$('.chat-bubble-chatbox.online').removeClass('d-none');
	} else {
		$('.chat-bubble-chatbox.online').removeClass('d-none');
		$('#livechat-chatbox-submit').click();
	}
}

var opn_live_chat = () => {
	// var session = require('web.session');
	// var user = session.uid
	$.ajax({
		url: "/live/chatbox/portaluser",
		type: 'POST',
		data: {},
		async: false,
		success: function (result) {
			var resultJSON = jQuery.parseJSON(result);
			if (resultJSON['uname'] != '') {
				$(chat_fname)[0].value = resultJSON['uname']
				$(chat_email)[0].value = resultJSON['email']
				$(chat_mobile)[0].value = resultJSON['mobile']

			}

		},
	});

	open_chat_box();
}

var opn_chat_request_callback = () => {
	open_chat_box();
	$('#chat_fname').val($('#request_callback_Section_forn #full_name').val());
	$('#chat_email').val($('#request_callback_Section_forn #email').val());
	$('#chat_mobile').val($('#request_callback_Section_forn #phone').val());

	$('.o_thread_window.o_in_home_menu').click();
}

var opn_chat_request_callback_callbtn = () => {
	$.get('/get/current/company/phone', {
		'event_id': event_id,
	}).done(function (result) {
		var template = document.getElementById('EventTemplateForModalPreview').innerHTML;
		var compiled_template = Handlebars.compile(template);
		var rendered = compiled_template(result[0]);
		document.getElementById('EventTemplateForModalPreviewContent').innerHTML = rendered;
		$('#event-fullybooked-popup').modal();
	});
}

var minimize_live_chat = () => {
	$('.chat-bubble-chatbox.online').addClass('d-none');
	$('.chat-bubble-chatbox.no-online').addClass('d-none');
}

var bubble_live_chat = () => {
	$('.chat-bubble-wrapper').addClass('d-none');
}

var bubble_live_open_chat = () => {
	$('.chat-bubble-wrapper').removeClass('d-none');
}

var onsubmit_live_chatbox_form = (el) => {
	$.ajax({
		url: "/onsubmit/live/chatbox",
		type: 'POST',
		data: {
			"fname": el.fname.value,
			"email": el.email.value,
			"phone": el.phone.value,
		},
		success: function (result) {
			var resultJSON = jQuery.parseJSON(result);
			if (resultJSON) {

			}
		},
	});

	return false;
}

var open_live_chat = () => {
	opn_live_chat()
}


// odoo.define('im_livechat.livesupport', function (require) {

//     var rootWidget = require('root.widget');
//     var im_livechat = require('im_livechat.legacy.im_livechat.im_livechat');
//     var button = new im_livechat.LivechatButton(
//         rootWidget,
//         "http://localhost:8068",
//         { "header_background_color": "#875A7B", "button_background_color": "#878787", "title_color": "#FFFFFF", "button_text_color": "#FFFFFF", "button_text": "Have a Question? Chat with us.", "input_placeholder": false, "default_message": "Hello, how may I help you?", "channel_name": "YourWebsite.com", "channel_id": 1, "current_partner_id": 3, "default_username": "Visitor", "chat_request_session": { "folded": false, "id": 25, "operator_pid": [3, "FRd"], "name": "Administrator, Administrator", "uuid": "28956b97-913e-4807-885b-9de29048048f", "type": "chat_request" } }
//     );
//     button.appendTo(document.body);
//     window.livechat_button = button;

// });


var click_start_whatsapp_chat = () => {
	

// 	$.ajax({
// 		url: "/company/whatsapp/mobile",
// 		type: 'POST',
// 		data: {
			
// 			"company_id": $('#request_callback_Section_forn #company_location_id_chat').val());
// ,		},
// 		success: function (result) {
// 			var resultJSON = jQuery.parseJSON(result);
// 			if (resultJSON) {

// 			}
// 		},
// 	});


	let empty = "";
	let fname = $('#request_callback_Section_forn #full_name').val();
	let email = $('#request_callback_Section_forn #email').val();
	let phone = $('#request_callback_Section_forn #phone').val();
	let whatapp =$('#request_callback_Section_forn #company_location_id_chat').val();
	let message_text = $('#message_text_callback_form').val();
	let url = window.location.href
	let msg = empty.concat("Name: ", fname, " ", "Mail: ", email, " ", "Mobile: ", phone , " ","Request from:" , url," ","Message:",message_text);
	let message = encodeURIComponent(msg);
	window.open("https://wa.me/"+whatapp+"?text=" + message, "_blank");



}

var click_start_whatsapp_chat_popup = () => {
	

// 	$.ajax({
// 		url: "/company/whatsapp/mobile",
// 		type: 'POST',
// 		data: {
			
// 			"company_id": $('#request_callback_Section_forn #company_location_id_chat').val());
// ,		},
// 		success: function (result) {
// 			var resultJSON = jQuery.parseJSON(result);
// 			if (resultJSON) {

// 			}
// 		},
// 	});


	let empty = "";
	let fname = $('.fname').val();
	let email = $('.email').val();
	let phone = $('.phone').val();
	let whatapp = $('#company_location_id_chatpop').val();
	let url = window.location.href
	let msg = empty.concat("Name: ", fname, " ", "Mail: ", email, " ", "Mobile: ", phone , " ","Request from:" , url);
	let message = encodeURIComponent(msg);
	window.open("https://wa.me/"+whatapp+"?text=" + message, "_blank");



}





// document.getElementById("livechat-chatbox-submit").onClick("click", () => {
// 	let chatopen = sessionStorage.getItem("chatopen");
// 	$('.o_livechat_button').remove();

// 	let ServerUrl = 'http://illuminations.pptssolutions.com/'
// 	let LiveChatOptions = {}
// 	let availablity = false

// 	var chatuser = $('.chatbox-frm .fname').val()
// 	chatuser1 = getStoredValue('chatuser');

// 	if (chatuser == '') {
// 		chatuser = getStoredValue('chatuser');
// 	} else if (chatuser !== chatuser1) {
// 		store_chatuser(chatuser)
// 	}


// 	$.ajax({
// 		url: "/livechat/get/session/channel",
// 		type: 'POST',
// 		async: false,
// 		data: {
// 			"fname": '',
// 			"email": $('.chatbox-frm .email').val(),
// 			"phone": $('.chatbox-frm .phone').val(),
// 		},
// 		success: function (result) {
// 			var resultJSON = jQuery.parseJSON(result);
// 			ServerUrl = resultJSON['server_url']
// 			LiveChatOptions = resultJSON['options']
// 			availablity = resultJSON['available']

// 			if (availablity != true) {

// 				$('.chat-bubble-chatbox.no-online').removeClass('d-none');
// 				$('.chat-bubble-chatbox.online').addClass('d-none');

// 			}
// 		},
// 	});


// 	if (availablity != false) {

// 		if (chatopen == 0) {


// 			sessionStorage.setItem("chatopen", 1);




// 			odoo.define('ppts_website_theme/static/src/js/livechat.js', function (require) {
// 				'use strict';

// 				require('bus.BusService');
// 				var concurrency = require('web.concurrency');
// 				var config = require('web.config');
// 				var core = require('web.core');
// 				var session = require('web.session');
// 				var time = require('web.time');
// 				var utils = require('web.utils');
// 				var Widget = require('web.Widget');

// 				var WebsiteLivechat = require('im_livechat.legacy.im_livechat.model.WebsiteLivechat');
// 				var WebsiteLivechatMessage = require('im_livechat.legacy.im_livechat.model.WebsiteLivechatMessage');
// 				var WebsiteLivechatWindow = require('im_livechat.legacy.im_livechat.WebsiteLivechatWindow');

// 				var AbstractMessage = require('im_livechat.legacy.mail.model.AbstractMessage');

// 				var _t = core._t;
// 				var QWeb = core.qweb;


// 				if (availablity != true) {


// 					try {
// 						self.displayNotification({
// 							message: _t("No available collaborator, please try again later."),
// 							sticky: true,
// 						});
// 					} catch (err) {
// 						/**
// 						 * Failure in displaying notification happens when
// 						 * notification service doesn't exist, which is the case in
// 						 * external lib. We don't want notifications in external
// 						 * lib at the moment because they use bootstrap toast and
// 						 * we don't want to include boostrap in external lib.
// 						 */
// 						console.warn(_t("No available collaborator, please try again later."));
// 					}
// 				}




// 				const { LivechatButton } = require('im_livechat.legacy.im_livechat.im_livechat');


// 				AbstractMessage.include({

// 					getDisplayedAuthor() {
// 						var user = this._super.apply(this, arguments) || this._defaultUsername;
// 						if (!user) {
// 							user = getStoredValue('chatuser');
// 						}
// 						return user;

// 					},


// 				});

// 				LivechatButton.include({
// 					className: `${LivechatButton.prototype.className}`,

// 					/**
// 					 * @override
// 					 */
// 					start() {

// 						// We trigger a resize to launch the event that checks if this element hides
// 						// a button when the page is loaded.
// 						$(window).trigger('resize');

// 						this.$el.append(`<script>

// 										setTimeout(() => {
// 											$('.o_livechat_button').click();
// 										}, 1);
										
// 										</script>`)

// 						this.$el.css("display", "none");

// 						return this._super(...arguments);
// 					},

// 					_openChat() {

// 						let chatopen = sessionStorage.getItem("chatopen");
// 						const o_in_home_menu = document.querySelectorAll('.o_in_home_menu');

// 						closechat(0)

// 						if (o_in_home_menu.length == 0) {
// 							sessionStorage.setItem("chatopen", 1);
// 							console.log('base openchat');
// 							//return this._super(...arguments);


// 							if (this._openingChat) {
// 								return;
// 							}
// 							var self = this;
// 							var cookie = utils.get_cookie('im_livechat_session');
// 							var def;
// 							this._openingChat = true;
// 							clearTimeout(this._autoPopupTimeout);
// 							if (cookie) {
// 								def = Promise.resolve(JSON.parse(cookie));
// 							} else {
// 								this._messages = []; // re-initialize messages cache


// 								var user = this.options.default_username

// 								if (!user) {
// 									user = getStoredValue('chatuser')
// 								}
// 								user = user + ' ~'
// 								def = session.rpc('/im_livechat/get_session', {
// 									channel_id: this.options.channel_id,
// 									anonymous_name: user,
// 									previous_operator_id: this._get_previous_operator_id(),
// 								}, { shadow: true });
// 							}
// 							def.then((livechatData) => {
// 								if (!livechatData || !livechatData.operator_pid) {
// 									try {
// 										self.displayNotification({
// 											message: _t("No available collaborator, please try again later."),
// 											sticky: true,
// 										});
// 									} catch (err) {
// 										/**
// 										 * Failure in displaying notification happens when
// 										 * notification service doesn't exist, which is the case in
// 										 * external lib. We don't want notifications in external
// 										 * lib at the moment because they use bootstrap toast and
// 										 * we don't want to include boostrap in external lib.
// 										 */
// 										console.warn(_t("No available collaborator, please try again later."));
// 									}
// 								} else {

// 									var username = livechatData['name']
// 									var result = ''

// 									if (username) {
// 										if (username.includes("Website Visitor") == true) {
// 											result = getStoredValue('chatuser') + ' ' + username;
// 										} else {

// 											result = username;

// 										}
// 									}

// 									livechatData['name'] = result;
// 									self._livechat = new WebsiteLivechat({
// 										parent: self,
// 										data: livechatData
// 									});
// 									return self._openChatWindow().then(function () {
// 										if (!self._history) {
// 											self._sendWelcomeMessage();
// 										}
// 										self._renderMessages();
// 										self.call('bus_service', 'addChannel', self._livechat.getUUID());
// 										self.call('bus_service', 'startPolling');

// 										utils.set_cookie('im_livechat_session', utils.unaccent(JSON.stringify(self._livechat.toData())), 60 * 60);
// 										utils.set_cookie('im_livechat_auto_popup', JSON.stringify(false), 60 * 60);
// 										if (livechatData.operator_pid[0]) {
// 											// livechatData.operator_pid contains a tuple (id, name)
// 											// we are only interested in the id
// 											var operatorPidId = livechatData.operator_pid[0];
// 											var oneWeek = 7 * 24 * 60 * 60;
// 											utils.set_cookie('im_livechat_previous_operator_pid', operatorPidId, oneWeek);
// 										}
// 									});
// 								}
// 							}).then(function () {
// 								self._openingChat = false;
// 							}).guardedCatch(function () {
// 								self._openingChat = false;
// 							});




// 						}

// 					},


// 					/**
// 				   * @override
// 				   * Called when the visitor closes the livechat chatter the first time (first click on X button)
// 				   * this will deactivate the mail_channel, clean the chat request if any
// 				   * and allow the operators to send the visitor a new chat request
// 				   */
// 					_onCloseChatWindow: function (ev) {
// 						closechat(1)
// 						$('.chat-bubble-wrapper').removeClass('d-none');
// 						$('.chat-bubble-wrapper').attr('open_new', 1);
// 						this._super(ev);
// 					},



// 				});
// 			});



// 			//$('.o_in_home_menu').remove();


// 			odoo.define('im_livechat.livesupport', (require) => {

// 				$('.o_in_home_menu').remove();

// 				let rootWidget = require('root.widget');
// 				let im_livechat = require('im_livechat.legacy.im_livechat.im_livechat');

// 				var button = new im_livechat.LivechatButton(
// 					rootWidget, ServerUrl, LiveChatOptions
// 				);

// 				button.appendTo(document.body);
// 				window.livechat_button = button;

// 				/*
// 				 setTimeout(() => {
// 					  //sessionStorage.setItem("chatopen", 0);
// 						$('.o_livechat_button').click();
// 						window.livechat_button._openChat();
// 				  }, 300);
				  
// 				  */


// 			});





// 		} else {
// 			//window.livechat_button.init();
// 			window.livechat_button._openChat();

// 			console.log(livechat_button);

// 		}


// 		minimize_live_chat()
// 		bubble_live_chat()

// 	}

// 	//window.livechat_button._openChat();



// });



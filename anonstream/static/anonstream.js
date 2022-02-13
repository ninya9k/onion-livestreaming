/* insert js-only markup */
const jsmarkup_info_title = '<header id="info__title" data-js="true"></header>';
const jsmarkup_chat_messages = '<ul id="chat-messages" data-js="true"></ul>';
const jsmarkup_chat_form = `\
  <form id="chat-form" data-js="true" action="/chat" method="post">
    <input id="chat-form__nonce" type="hidden" name="nonce" value="">
    <textarea id="chat-form__message" name="message" maxlength="512" required placeholder="Send a message..." rows="1"></textarea>
    <div id="chat-live">
      <span id="chat-live__ball"></span>
      <span id="chat-live__status">Not connected to chat</span>
    </div>
    <input id="chat-form__submit" type="submit" value="Chat" disabled>
  </form>`;

const insert_jsmarkup = () => {
    if (document.getElementById("info__title") === null) {
        const parent = document.getElementById("info");
        parent.insertAdjacentHTML("beforeend", jsmarkup_info_title);
    }
    if (document.getElementById("chat-messages") === null) {
        const parent = document.getElementById("chat__messages");
        parent.insertAdjacentHTML("beforeend", jsmarkup_chat_messages);
    }
    if (document.getElementById("chat-form") === null) {
        const parent = document.getElementById("chat__form");
        parent.insertAdjacentHTML("beforeend", jsmarkup_chat_form);
    }
}

insert_jsmarkup();

/* create websocket */
const info_title = document.getElementById("info__title");
const chat_messages_parent = document.getElementById("chat__messages");
const chat_messages = document.getElementById("chat-messages");
const on_websocket_message = (event) => {
    const receipt = JSON.parse(event.data);
    switch (receipt.type) {
        case "error":
            console.log("server sent error via websocket", receipt);
            break;

        case "init":
            console.log("init", receipt);
            chat_form_nonce.value = receipt.nonce;
            info_title.innerText = receipt.title;
            break;

        case "title":
            console.log("title", receipt);
            info_title.innerText = receipt.title;
            break;

        case "ack":
            console.log("ack", receipt);
            if (chat_form_nonce.value === receipt.nonce) {
                chat_form_message.value = "";
            } else {
                console.log("nonce does not match ack", chat_form_nonce, receipt);
            }
            chat_form_submit.disabled = false;
            chat_form_nonce.value = receipt.next;
            break;

        case "chat":
            const chat_message = document.createElement("li");
            chat_message.classList.add("chat-message");

            const chat_message_name = document.createElement("span");
            chat_message_name.classList.add("chat-message__name");
            chat_message_name.innerText = receipt.name;
            chat_message_name.style.color = receipt.color

            const chat_message_text = document.createElement("span");
            chat_message_text.classList.add("chat-message__text");
            chat_message_text.innerText = receipt.text;

            chat_message.insertAdjacentElement("beforeend", chat_message_name);
            chat_message.insertAdjacentHTML("beforeend", ":&nbsp;");
            chat_message.insertAdjacentElement("beforeend", chat_message_text);

            chat_messages.insertAdjacentElement("beforeend", chat_message);
            chat_messages_parent.scrollTo({
                left: 0,
                top: chat_messages_parent.scrollTopMax,
                behavior: "smooth",
            });

            console.log("chat", receipt);
            break;

        default:
            console.log("incomprehensible websocket message", message);
    }
};
const chat_live_ball = document.getElementById("chat-live__ball");
const chat_live_status = document.getElementById("chat-live__status");
let ws;
let websocket_backoff = 2000; // 2 seconds
const connect_websocket = () => {
    if (ws !== undefined && (ws.readyState === ws.CONNECTING || ws.readyState === ws.OPEN)) {
        console.log("refusing to open another websocket");
        return;
    }
    chat_live_ball.style.borderColor = "gold";
    chat_live_status.innerText = "Connecting to chat...";
    ws = new WebSocket(`ws://${document.domain}:${location.port}/live`);
    ws.addEventListener("open", (event) => {
        chat_form_submit.disabled = false;
        chat_live_ball.style.borderColor = "green";
        chat_live_status.innerText = "Connected to chat";
        websocket_backoff = 2000; // 2 seconds
    });
    ws.addEventListener("close", (event) => {
        chat_form_submit.disabled = true;
        chat_live_ball.style.borderColor = "maroon";
        chat_live_status.innerText = "Disconnected from chat";
        setTimeout(connect_websocket, websocket_backoff);
        websocket_backoff = Math.min(32000, websocket_backoff * 2);
        console.log("websocket closed", event);
    });
    ws.addEventListener("error", (event) => {
        chat_form_submit.disabled = true;
        chat_live_ball.style.borderColor = "maroon";
        chat_live_status.innerText = "Error connecting to chat";
        console.log("websocket error", event);
    });
    ws.addEventListener("message", on_websocket_message);
}

connect_websocket();

/* override js-only chat form */
const chat_form = document.getElementById("chat-form");
const chat_form_nonce = document.getElementById("chat-form__nonce");
const chat_form_message = document.getElementById("chat-form__message");
const chat_form_submit = document.getElementById("chat-form__submit");
chat_form.addEventListener("submit", (event) => {
    event.preventDefault();
    const payload = {message: chat_form_message.value, nonce: chat_form_nonce.value};
    chat_form_submit.disabled = true;
    ws.send(JSON.stringify(payload));
});
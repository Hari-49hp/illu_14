function onsubmit_general_enquiry(el)
{
    document.getElementsByClassName("chatbox-frm").fname.value=el.customer_fullname.value;
    document.getElementsByClassName("chatbox-frm").email.value=el.customer_email.value;
    document.getElementsByClassName("chatbox-frm").phone.value=el.customer_phone.value;
    opn_live_chat();

    return false;
}
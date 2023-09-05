const validateEmail = (email) => {
    return email.match(
        /^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/
    );
};

const validate = () => {
    const $result = $('#newsletter-result');
    const email = $('#newsletter-email').val();
    $result.text('');

    console.log(validateEmail(email), 'yyyyyy-------------');

    if (validateEmail(email)) {
        document.getElementById("newsletterformfooter").submit();
        $('#newsletter-thankyou-popup').modal();
        $('#newsletter-email').val('');
        $('#newsletter-result').addClass('mbl-d-none');
    } else {
        $result.text('*Email is not valid');
        $('#newsletter-result').removeClass('mbl-d-none');
    }
    return false;
}

var newsletterform = () => {
    validate()
}
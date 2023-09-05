$(document).ready(function () {
    $('#testimonial_type').val('text');
    $('#testimonial_employee_type').val('all');
    $('#testimonial_service_categ_id').val('all');
});

let testimonial_view_type = (view) => {
    if (view.value === 'video') {
        $('.testomonial-videocard').removeClass('d-none');
        $('.testomonial-list-card').addClass('d-none');
    }
    else {
        $('.testomonial-videocard').addClass('d-none');
        $('.testomonial-list-card').removeClass('d-none');
    }
}

let on_change_testimonial_filter = () => {
    let list_view = document.querySelectorAll('.testomonial-list-card');
    let card_view = document.querySelectorAll('.testomonial-listcard');

    let employee_type = $('#testimonial_employee_type').val();
    let service_type = $('#testimonial_service_categ_id').val();


    let filter = (element) => {
        let attr_employee = $(element).data("employee-type");
        let attr_service = String($(element).data("service-type"));

        if (employee_type === 'all' && service_type === 'all') {
            element.style.display = "grid";
        }
        else if (employee_type === 'all' && service_type === attr_service) {
            element.style.display = "grid";
        }
        else if (employee_type != 'all' && attr_employee.includes(parseInt(employee_type)) && service_type === 'all') {
            element.style.display = "grid";
        }
        else if (employee_type != 'all' && service_type == attr_service && attr_employee.includes(parseInt(employee_type))) {
            console.log('No All');
            element.style.display = "grid";
        }
        else {
            element.style.display = "none";
        }
    }

    list_view.forEach(element => {
        filter(element)
    });

    card_view.forEach(element => {
        filter(element)
    });
}

let mobile_filter = () => {
    $('.heading-right-fields').addClass('mobile-model-sidefilter navbarmaincont sidenav activemenu');
}

let mobile_filter_close = () => {
    $('.heading-right-fields').removeClass('mobile-model-sidefilter navbarmaincont sidenav activemenu');
}
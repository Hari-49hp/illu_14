# -*- coding: utf-8 -*-
{
    'name': 'PPTS: Website Theme',
    'description': 'A description for your theme.',
    'version': '1.0',
    'author': 'PPTS',
    'data': [
        'security/ir.model.access.csv',

        'views/assets.xml',
        'views/snippet.xml',
        'views/website_menu.xml',
        'views/master.xml',
        'views/website_faq_views.xml',
        'views/res_company_views.xml',
        'views/feedback_category_view.xml',
        'views/helpdesk_ticket.xml',

        #common
        'snippet/aboutus.xml',
        'snippet/our_team.xml',
        'snippet/team_therapists.xml',
        'snippet/contact_us.xml',
        'snippet/faq.xml',
        'snippet/testimonials.xml',
        'snippet/press_media.xml',
        'snippet/career.xml',
        'snippet/career_therapist.xml',
        'snippet/career_management.xml',
        'snippet/success_form.xml',
        'snippet/blog.xml',
        'snippet/blog_single.xml',
        'snippet/event.xml',
        'snippet/event_single.xml',
        'snippet/inactive.xml',
        'snippet/live_chat.xml',
        'snippet/popup.xml',
        'snippet/header.xml',
        'snippet/footer.xml',
        'snippet/student.xml',
        'snippet/holistichealing.xml',
        # 'snippet/healing_approaches.xml',
        'snippet/training_main_page.xml',
        'snippet/initial_application_form.xml',
        'snippet/management_application_form.xml',
        'snippet/meditation.xml',
        'snippet/therapy.xml',
        'snippet/therapy_category.xml',
        'snippet/corporate_wellness.xml',
        'snippet/training_individual_page.xml',
        'snippet/healing_apprpage.xml',
        'snippet/retreats.xml',
        'snippet/wellness_retreats.xml',
        'snippet/wellness_retreats_all.xml',
        'snippet/wellness_retreats_single.xml',
        'snippet/request_callback.xml',
        'snippet/checkout_book_an_event.xml',
        'snippet/cart.xml',
        # 'snippet/event_payment.xml',

        # Homepage
        'snippet/homepage/header.xml',
        'snippet/homepage/about.xml',
        'snippet/homepage/service.xml',
        'snippet/homepage/upcoming_event.xml',
        'snippet/homepage/participents.xml',
        'snippet/homepage/our_experts.xml',
        'snippet/homepage/achivements.xml',
        'snippet/homepage/featured_in.xml',
        'snippet/homepage/client_about.xml',
        'snippet/homepage/blog.xml',
        'snippet/homepage/book_free_apt.xml',

        # About
        'snippet/aboutus/awards_recognition.xml',
        'snippet/aboutus/insipiring_values.xml',
        'snippet/aboutus/mission_vision.xml',
        'snippet/aboutus/our_approach.xml',
        'snippet/aboutus/our_journey.xml',
        'snippet/aboutus/our_story.xml',
        'snippet/aboutus/power_lies_within.xml',

        # Team
        'snippet/team/our_team.xml',
        'snippet/team/therapists.xml',

        # Team Therapists
        'snippet/team_therapist/featured_post.xml', 
        'snippet/team_therapist/about.xml',
        'snippet/team_therapist/certifications.xml', 
        'snippet/team_therapist/insipiring_values.xml', 
        'snippet/team_therapist/mission.xml',
        'snippet/team_therapist/offer.xml',
        'snippet/team_therapist/services.xml', 
        'snippet/team_therapist/upcoming_event.xml', 

        # Press And Media
        'snippet/press_media/header.xml',
        'snippet/press_media/featured_in.xml',
        'snippet/press_media/articles.xml',

        # Search

        'snippet/search/search.xml',
        'snippet/search/result.xml',

        #Event
        'snippet/upcoming_event/upcoming_event.xml',

        # Contact Us
        'snippet/contact/careers.xml',
        'snippet/contact/corporates.xml',
        'snippet/contact/customer_care.xml',
        'snippet/contact/enquiry_form.xml',
        'snippet/contact/franchise_info.xml',
        'snippet/contact/general_inquiry.xml',
        'snippet/contact/header.xml',


        #parking Detail
        'snippet/parking_details.xml',

        # Blogs
        'snippet/blogs/blog.xml',
        # 'snippet/homepage.xml',

        #Meditation
        'snippet/meditation/header.xml',
        'snippet/meditation/video_post.xml',
        'snippet/meditation/type_of_meditation.xml',
        'snippet/meditation/free_intro.xml',
        'snippet/meditation/common_myth.xml',
        'snippet/meditation/why_need_this.xml',
        'snippet/meditation/shop.xml',
        'snippet/meditation/meditation_event.xml',

        #Therapy
        'snippet/therapy/header.xml',
        'snippet/therapy/help.xml',
        'snippet/therapy/browse.xml',
        'snippet/therapy/journey.xml',
        'snippet/therapy/booking.xml',
        'snippet/therapy/approch.xml',
        'snippet/therapy/how_we_work.xml',

        #Therapy_category
        'snippet/therapy_category/header.xml',
        'snippet/therapy_category/journey.xml',
        'snippet/therapy_category/booking.xml',
        'snippet/therapy_category/categ_therapist.xml',
        'snippet/therapy_category/solutions.xml',
        'snippet/therapy_category/relationship_healing.xml',
        'snippet/therapy_category/support.xml',

        #Data
        'data/faq_email_template.xml',
        'data/career_email_template.xml',
        'data/enquiry_email_template.xml',
        
        #Appointment
        'snippet/checkout/appointment.xml',
        'snippet/checkout/appointment_payment_success.xml',
        'snippet/checkout/appointment_payment_template.xml',
        'snippet/checkout/event_checkout.xml',
        'snippet/checkout/event_payment_success.xml',



    ],
    'category': 'Theme/Creative',
    'depends': [
                'base', 'website', 'hr', 'mass_mailing' , 'website_slides', 'website_google_map', 'ppts_custom_apt_mgmt', 
                'helpdesk', 'website_hr_recruitment', 'website_blog', 'im_livechat', 'ppts_custom_hr',
                'pos_event_management', 'website_sale'
                ],
    'qweb': ['static/src/xml/live_chat.xml'],
}

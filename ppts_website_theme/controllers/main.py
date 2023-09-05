from odoo import http, tools, _
from odoo.http import request, Response
import odoo
import odoo.modules.registry
import calendar
from odoo.addons.web.controllers.main import ensure_db, Home
from odoo.addons.http_routing.models.ir_http import slug,unslug
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.website_event.controllers.main import WebsiteEventController
from odoo.addons.website_event_sale.controllers.main import WebsiteEventSaleController
from odoo.addons.im_livechat.controllers.main import LivechatController
from datetime import datetime, timedelta
import json, werkzeug
from itertools import groupby
import requests
import urllib.request
import urllib
from bs4 import BeautifulSoup
from ast import literal_eval
from odoo import fields, http, _
from datetime import datetime
import logging
import base64
import pytz
import io
import re

_logger = logging.getLogger(__name__)


class LivechatController(LivechatController):
    @http.route('/im_livechat/load_templates', type='json', auth='none', cors="*")
    def load_templates(self, **kwargs):
        base_url = request.httprequest.base_url
        templates = [
            'ppts_website_theme/static/src/xml/legacy/live_chat.xml',
        ]
        return [tools.file_open(tmpl, 'rb').read() for tmpl in templates]

class WebsiteCalendar(http.Controller):
    @http.route(['/live/chatbox/portaluser'], type='http', auth="public", website=True, csrf=False, cros='*')
    def livechat_portaluser(self, **post):
        user_id = request.env.uid
        if user_id:
            users = request.env['res.users'].sudo().search([('id','=',user_id)])
            values = {'uname':users.partner_id.name or '','email':users.partner_id.email or '','mobile':users.partner_id.mobile or ''}
        else:
            values = {}
        return json.dumps(values)


class AuthLoginCustomHome(Home):
    @http.route('/web/login', type='http', auth="none", csrf=False)
    def web_login(self, redirect=None, **kw):
        ensure_db()
        request.params['login_success'] = False

        if not request.uid:
            request.uid = odoo.SUPERUSER_ID

        values = request.params.copy()
        try:
            values['databases'] = http.db_list()
        except odoo.exceptions.AccessDenied:
            values['databases'] = None

        if request.httprequest.method == 'POST':
            old_uid = request.uid
            try:
                uid = request.session.authenticate(request.session.db, request.params['login'], request.params['password'])
                request.params['login_success'] = True
                return http.redirect_with_hash(self._login_redirect(uid, redirect=redirect))
            except odoo.exceptions.AccessDenied as e:
                request.uid = old_uid
                if e.args == odoo.exceptions.AccessDenied().args:
                    values['error'] = _("Wrong login/password")
                else:
                    values['error'] = e.args[0]
        else:
            if 'error' in request.params and request.params.get('error') == 'access':
                values['error'] = _('Only employees can access this database. Please contact the administrator.')

        if 'login' not in values and request.session.get('auth_login'):
            values['login'] = request.session.get('auth_login')

        if not odoo.tools.config['list_db']:
            values['disable_database_manager'] = True

        response = request.render('web.login', values)
        response.headers['X-Frame-Options'] = 'DENY'
        return werkzeug.utils.redirect('/')

class WebsiteCalendar(http.Controller):
    @http.route(['/wiz/web/login'], type='http', auth="none", csrf=False)
    def wiz_web_login(self, redirect=None, **kw):
        ensure_db()
        request.params['login_success'] = 'false'

        values = request.params.copy()

        if request.httprequest.method == 'POST':
            old_uid = request.uid
            try:
                uid = request.session.authenticate(request.session.db, kw['login'], kw['password'])
            except odoo.exceptions.AccessDenied as e:
                request.uid = old_uid
                if e.args == odoo.exceptions.AccessDenied().args:
                    values['status'] = 'worng'
                    values['error'] = _("Wrong login/password")
                else:
                    values['status'] = 'worng'
                    values['error'] = _("Wrong login/password")

        else:
            values['status'] = 'pass'
        
        return json.dumps(values)

    @http.route(['/theme/upcoming_event/render'], type='http', auth="public", website=True, csrf=False)
    def theme_upcoming_event_render(self, **post):
        dict1 = {}; event = []
        if post and 'date' in post:
            evnt_date = datetime.strptime(post['date'], "%Y-%m-%d").date()
            event_ids = request.env['event.event'].sudo().search([("stage_id",'in',('Published','Announced'))])
            for i in event_ids:
                book_btn = """ 
                        <a class="borderedbtn" style="color: #00AEC7 !important;" href="#book_free_apt_snippet">Enquire Now</a>
                        <a class="fullbutton" id="selected-event-ID" data-event-id="%s" > Book Now </a>
                    """ % ( i.id )
                event_reg = request.env['event.registration'].search([('event_id','=',i.id)])
                if i.seats_limited == True and i.seats_max <= len(event_reg.ids):
                    book_btn = """ 
                        <a class="borderedbtn" style="color: #00AEC7 !important;" onclick="eventJoinWaitingList(%s)">Join Waiting List</a>
                        <a class="fullbutton event-fully-booked-calendar" onclick="eventAllBookedModal(%s)"> All Booked </a>
                    """ % (str(i.id), str(i.id))
                for t in i.multi_date_line_ids:
                    if t.date_begin == evnt_date:
                        facilitator_id = i.facilitator_evnt_ids[0].id

                        type_event = ''; type_event_set = ''
                        if i.type_event == 'type_online': type_event = 'Online'; type_event_set = 'online'
                        elif i.type_event == 'type_onsite': type_event = 'Onsite'; type_event_set = 'onsite'
                        elif i.type_event == 'type_hybrid': type_event = 'Hybrid'; type_event_set = 'online/onsite'
                        
                        tz = request.env.user.tz or pytz.utc;
                        timezone = pytz.timezone(tz or 'UTC')
                        date_begin = t.m_date_begin.replace(tzinfo=pytz.timezone('UTC')).astimezone(timezone)
                        date_end = t.m_date_begin.replace(tzinfo=pytz.timezone('UTC')).astimezone(timezone)

                        dict1[i.id] = {
                            'name': i.name or '',
                            'event_id': i.id,
                            'date': date_begin.date().strftime("%d %B") or '',
                            'time': t.hour_time_begin+':'+t.min_time_begin +' To '+ t.hour_time_end+':'+t.min_time_end or '',
                            'location': i.company_id.name or '',
                            'location_id': i.company_id.id,
                            'location_abbreviation': i.company_id.abbreviation,
                            'event_category_id': i.event_type_id.id,
                            'service_category_id': i.event_service_categ_id.id,
                            'facilitator': i.get_facilitator_name() or '',
                            'facilitator_id': facilitator_id,
                            'type': type_event or '',
                            'event_category': i.event_type_id.name or 'NO',
                            'sub_category': i.event_sub_categ_id.name or 'NO',
                            'type_event': dict(i._fields['type_event'].selection).get(i.type_event),
                            'type_event_str': type_event_set,
                            'price': i.get_event_price(),
                            'evt_url': '/event/'+slug(i)+'/register',
                            'image': '/web/image?model=event.event&amp;id=%s&amp;field=image' % (i.id) if  i.image else '/ppts_website_theme/static/src/img/post1.png',
                            # 'page': post['calendar_domain'] or '',
                            'employee_ids': str(i.facilitator_evnt_ids.ids),
                            'book_btn': book_btn
                        }
            return json.dumps(dict1)
    
    @http.route(['/get/event/modal/calendar'], type='http', auth="public", website=True, csrf=False)
    def theme_get_event_modal_calendar(self, **post):
        print('post-------->',post)
        i = request.env['event.event'].sudo().browse(int(post['event_id'])); event = []
        # for t in i.multi_date_line_ids:
        facilitator_name = ''
        for j in i.facilitator_evnt_ids:
            facilitator_name += j.name+','
        facilitator_name = facilitator_name[:-1]
        
        tz = request.env.user.tz or pytz.utc;
        timezone = pytz.timezone(tz or 'UTC')
        date_begin = i.multi_date_line_ids[0].m_date_begin.replace(tzinfo=pytz.timezone('UTC')).astimezone(timezone)
        date_end = i.multi_date_line_ids[-1].m_date_end.replace(tzinfo=pytz.timezone('UTC')).astimezone(timezone)
        facilitator_id = i.facilitator_evnt_ids[0].id

        event.append({
            'name': i.name or '',
            'event_id': i.id,
            'date': date_begin.date().strftime("%Y-%m-%d") + 'To' + date_end.date().strftime("%Y-%m-%d") ,
            'event_dates': date_begin.date().strftime("%d %B") + 'To' + date_end.date().strftime("%d %B") if i.event_multiple_date == 'multiday' else date_begin.date().strftime("%d %B"),
            'time': i.multi_date_line_ids[0].hour_time_begin+':'+i.multi_date_line_ids[0].min_time_begin +' To '+ i.multi_date_line_ids[-1].hour_time_end+':'+i.multi_date_line_ids[-1].min_time_end or '',
            'location': i.company_id.name or '',
            'facilitator': i.facilitator_evnt_ids[0].name or '',
            'facilitator_id': facilitator_id,
            'event_category': i.event_type_id.name or 'NO',
            'sub_category': i.event_sub_categ_id.name or 'NO',
            'location_id': i.company_id.id,
            'location_abbreviation': i.company_id.abbreviation,
            'event_category_id': i.event_type_id.id,
            'service_category_id': i.event_service_categ_id.id,
            'type_event': dict(i._fields['type_event'].selection).get(i.type_event),
            'title': i.name or '',
            'start': date_begin.date().strftime("%Y-%m-%d")+'T'+i.multi_date_line_ids[0].hour_time_begin+':'+i.multi_date_line_ids[0].min_time_begin,
            'end': date_begin.date().strftime("%Y-%m-%d")+'T'+i.multi_date_line_ids[-1].hour_time_end+':'+i.multi_date_line_ids[-1].min_time_end,
            'date': date_begin.date().strftime("%Y-%m-%d"),
            'price': i.get_event_price(),
            'evt_url': '/event/'+slug(i)+'/register',
            'background_color': i.event_service_categ_id.color_code or '#F7EADB',
            'image': '/web/image?model=event.event&amp;id=%s&amp;field=image' % (i.id) if  i.image else '/ppts_website_theme/static/src/img/mstp1.jpg',
            # 'page': post['calendar_domain'] or ''
            })
        event.sort(key=lambda x: x["start"])
        return json.dumps(event)

    @http.route(['/action/join/event/ticket/waitinglist/<int:event_id>'], type='http', auth="public", website=True, csrf=False)
    def theme_action_join_event_ticket_waitinglist(self, event_id=None, **post):
        request.env['event.registration'].sudo().create({
            'event_id': event_id,
            'name': post['name'],
            'email': post['email'],
            'mobile': post['phone'],
        })
        msg = 'Thanks for submiting your request you will be in waiting list for now, We will get back to you soon '+ post['email']
        return http.request.render("ppts_website_theme.theme_success_page", {"title": 'You Are In Waiting List!',"msg":msg})

    @http.route(['/theme/upcoming_event/render/reach'], type='http', auth="public", website=True, csrf=False)
    def theme_upcoming_event_render_reach(self, **post):
        dict1 = {}; event = []
        event_ids = request.env['event.event'].sudo().search([("stage_id",'in',('Published','Announced'))])
        for i in event_ids:
            # if i.date_begin.date() == evnt_date:
            for t in i.multi_date_line_ids:
                # if i.s_start_date == evnt_date:
                facilitator_name = ''
                for j in i.facilitator_evnt_ids:
                    facilitator_name += j.name+','
                facilitator_name = facilitator_name[:-1]
                type_event = '';type_event_set = ''
                if i.type_event == 'type_online': type_event = 'Online'; type_event_set = 'online'
                elif i.type_event == 'type_onsite': type_event = 'Onsite'; type_event_set = 'onsite'
                elif i.type_event == 'type_hybrid': type_event = 'Hybrid'; type_event_set = 'online/onsite'
                
                tz = request.env.user.tz or pytz.utc;
                timezone = pytz.timezone(tz or 'UTC')
                date_begin = t.m_date_begin.replace(tzinfo=pytz.timezone('UTC')).astimezone(timezone)
                date_end = t.m_date_end.replace(tzinfo=pytz.timezone('UTC')).astimezone(timezone)
                facilitator_id = i.facilitator_evnt_ids[0].id
                event.append({
                    'name': i.name or '',
                    'event_id': i.id,
                    'date': date_begin.date().strftime("%Y-%m-%d") or '',
                    'time': t.hour_time_begin+':'+t.min_time_begin +' To '+ t.hour_time_end+':'+t.min_time_end or '',
                    'location': i.company_id.name or '',
                    'facilitator': facilitator_name or '',
                    'facilitator_id': facilitator_id,
                    'type': type_event or '',
                    'event_category': i.event_type_id.name or 'NO',
                    'sub_category': i.event_sub_categ_id.name or 'NO',
                    'location_id': i.company_id.id,
                    'location_abbreviation': i.company_id.abbreviation,
                    'event_category_id': i.event_type_id.id,
                    'service_category_id': i.event_service_categ_id.id,
                    'type_event': dict(i._fields['type_event'].selection).get(i.type_event),
                    'type_event_str': type_event_set,
                    'title': i.name or '',
                    'start': date_begin.date().strftime("%Y-%m-%d")+'T'+t.hour_time_begin+':'+t.min_time_begin,
                    'end': date_begin.date().strftime("%Y-%m-%d")+'T'+t.hour_time_end+':'+t.min_time_end,
                    'date': date_begin.date().strftime("%Y-%m-%d"),
                    'price': i.get_event_price(),
                    'evt_url': '/event/'+slug(i)+'/register',
                    'background_color': i.event_service_categ_id.color_code or '#F7EADB',
                    # 'page': post['calendar_domain'] or ''
                })

        event.sort(key=lambda x: x["start"])
        # event.sort(key=lambda x: datetime.strptime(time_data, '%Y-%m-%d'))
        return json.dumps(event)

    @http.route(['/team'], type='http', auth="public", website=True, csrf=False)
    def theme_our_therapist_team(self, **post):
        values = {};av = {};av_l = [];aos_delay = 200
        emp_typ = request.env['hr.employee.category'].sudo().search([('name', '=', 'Therapist')])
        hr_ids = request.env['hr.employee'].sudo().search([('employee_type', 'in', emp_typ.ids)])
        for i in hr_ids:
            job_position = ''
            for job in i.by_support: job_position += '&'+job.name
            av = {
                'image_1920': i.image_1920,
                'name': i.name,
                'job_position': job_position[1:],
                'company_name': i.company_id.name,
                'aos_delay': aos_delay,
                'id': i.id,
            }
            av_l.append(av); aos_delay += 100

        values = {'employee_type':av_l}
        return request.render('ppts_website_theme.our_team_page', values)
    
    @http.route(['/team/filter'], type='http', auth="public", website=True, csrf=False)
    def theme_team_filter(self, **post):
        domain = [];av = {};av_l = {};aos_delay = 200;platform_list=[post['by_platform']]
        # domain append based on current requirement 17/11/2022
        if 'by_platform' in post and post['by_platform'] == 'online' or 'onsite':
            platform_list.append('online/onsite')
            domain.append(('by_platform','in',platform_list))
        if 'by_platform' in post and post['by_platform'] == 'online/onsite':
            platform_list.append('online')
            platform_list.append('onsite')
            domain.append(('by_platform','in',platform_list))
        # domain append based on current requirement 17/11/2022

        if 'by_support' in post and post['by_support'] != '[]':
            by_support = post['by_support'][1:-1].split(',')
            if by_support:
                by_support = [int(item[1:-1]) for item in by_support]
                domain.append(('by_support','in',by_support))
        
        if 'by_solution' in post and post['by_solution'] != '[]':
            by_solution = post['by_solution'][1:-1].split(',')
            if by_solution: 
                by_solution = [int(item[1:-1]) for item in by_solution]
                domain.append(('by_solution','in',by_solution))

        if 'by_location' in post and post['by_location'] != '[]':
            by_location = post['by_location'][1:-1].split(',')
            if by_location: 
                by_location = [int(item[1:-1]) for item in by_location]

                domain.append(('company_id','in',by_location))
        emp_typ = request.env['hr.employee.category'].sudo().search([('name', '=', 'Therapist')])
        domain.append(('employee_type', 'in', emp_typ.ids))
        hr_ids = request.env['hr.employee'].sudo().search(domain, order='name asc')
        for i in hr_ids:
            available_id = request.env['availability.availability'].sudo().search([('date_range','=','ongoing'),\
                ('facilitator','=',i.id),('available_date','=',datetime.now().strftime('%Y-%m-%d'))])
            if 'only_available' in post and post['only_available'] == 'true' and available_id:
                job_position = ''
                for job in i.by_support: job_position += '&'+job.name
                av = {
                    'id': str(i.id),
                    'name': i.name,
                    'job_position': job_position[1:],
                    'company_name': i.company_id.name,
                    'aos_delay': aos_delay
                }
                av_l[i.id] = av; aos_delay += 100
            elif 'only_available' in post and post['only_available'] == 'false':
                job_position = ''
                for job in i.by_support: job_position += '|'+job.name
                av = {
                    'id': str(i.id),
                    'name': i.name,
                    'job_position': job_position[1:],
                    'company_name': i.company_id.name,
                    'aos_delay': aos_delay
                }
                av_l[i.name] = av; aos_delay += 100
        return json.dumps(av_l)


    @http.route(['/about'], type='http', auth="public", website=True)
    def theme_about_us(self, **post):
        return request.render('ppts_website_theme.aboutus_page')

    @http.route(['/contactus'], type='http', auth="public", website=True)
    def theme_contact_us(self, **post):
        company_details =[]
        company_ids = request.env['res.company'].sudo().search([('id','!=',1)],order='id asc')
        for each in company_ids:
            company_details.append({
                    'working_hour_start':each.working_hours_start,
                    'street':each.street,
                    'street2':each.street2,
                    'city':each.city,
                    'state_id':each.state_id.name or "",
                    'country_id':each.country_id.name or "",
                    'phone':each.phone,
                    'zip':each.zip,
                    'email':each.email,
                    'display_name':each.display_name,
                    'id':each.id
                })
        vals = {
                'data':company_details
        }
        return request.render('ppts_website_theme.contactus_page',vals)

    @http.route(['/team/therapists/<int:therapist_id>'], type='http', auth="public", website=True)
    def theme_our_team_therapist_team(self, therapist_id, **post):

        emp_id = request.env['hr.employee'].sudo().browse(therapist_id)

        values = {
            'emp_id': emp_id,
            'emp_name': str(emp_id.name) + "'s",
        }

        return request.render('ppts_website_theme.template_our_team_therapist_page', values)

    @http.route(['/upcoming/event'], type='http', auth="public", website=True)
    def theme_upcoming_event(self, **post):
        return request.render('ppts_website_theme.upcoming_event_page')

    @http.route(['/corporate'], type='http', auth="public", website=True)
    def theme_corporate_wellness(self, **post):
        return request.render('ppts_website_theme.theme_corporate_wellness')
        
    @http.route(['/blog/trending/latest'], type='http', auth="public", website=True)
    def theme_blog_post_short_latest_this_month(self, **post):
        return request.render('ppts_website_theme.blog_post_short_latest_this_month_treanding')

    @http.route(['/upcoming/event/location'], type='http', auth="public", website=True, csrf=False, cors='*')
    def upcomin_event_location(self, **post):
        dropdown = ''
        location_ids = request.env['venue.venue'].sudo().search([])
        for each_location in location_ids:
            dropdown += '<option value="'+ str(each_location.id) +'">'+ each_location.name +'</option>'
        return dropdown

    @http.route(['/faq'], type='http', auth="public", website=True)
    def theme_faq(self, **post):
        all = []; faq_lst = []

        all_faq = request.env['website.faq'].sudo().search([('website_publish','=',True)])
        for i in all_faq:
            all.append({
                'id': i.id,
                'title': i.name or ' ',
                'description': i.description or ' ',
            })

        tag_ids = request.env['faq.tags'].sudo().search([('website_publish','=',True)])
        for i in tag_ids:
            faq_ids = request.env['website.faq'].sudo().search([('faq_tag_ids','=',i.id)])
            lst = []
            for j in faq_ids:
                lst.append({
                    'id': j.id,
                    'title': j.name or ' ',
                    'description': j.description or ' ',
                })
                    
            faq_lst.append({
                'id': i.id,
                'faq_tab': lst,
            })

        values = {
            'all_faq':all,
            'faq_ids': faq_lst,
        }
        return request.render('ppts_website_theme.theme_faq_page',values)

    @http.route(['/testimonials'], type='http', auth="public", website=True)
    def theme_testimonials(self, **post):
        values = {};hr_categ = [];service_categ = [];tags = [];all_cards = [];testimonial_tags = {};
        hr_categ_ids = request.env['hr.employee.category'].sudo().search([])
        for i in hr_categ_ids:
            hr_categ.append({
                'id': i.id,
                'name': i.name or '',
            })

        service_categ_ids = request.env['appointment.category'].sudo().search([])
        for i in service_categ_ids:
            service_categ.append({
                'id': i.id,
                'name': i.name or '',
            })
        
        tag_ids = request.env['testimonial.tags'].sudo().search([('website_publish','=',True)])
        for i in tag_ids:
            tags.append({
                'id': i.id,
                'sequence': i.sequence or '',
                'name': i.name or '',
            })

        card_ids = request.env['testimonial'].sudo().search([('website_publish','=',True)])
        for i in card_ids:
            all_cards.append({
                'id': i.id,
                'title': i.name or '',
                'description': i.description or '',
                'customer_name': i.partner_id.name or '',
                'image_url': '/web/image?model=testimonial&id=%s&field=image_av' % (i.id) \
                    if i.image_av else '/ppts_website_theme/static/src/img/profile-empty-round.png',
                'video_url': i.video_url,
                'service_type': i.service_type.id,
                'employee_type': i.employee_type.ids
            })

        values = {
                'hr_categ_ids':hr_categ, 
                'service_categ_ids': service_categ, 
                'tag_ids': tags, 
                'all_cards': all_cards,
                'testimonial_tags': testimonial_tags,
            }
        return request.render('ppts_website_theme.theme_testimonials_page', values)
    
    @http.route(['/testimonial/categ-ajax'], type='http', auth="public", website=True, csrf=False)
    def testimonial_categ_ajax_method(self, **post):
        html_view = ''

        def get_video_embed_code(video_url):
            if not video_url:
                return False
            # To detect if we have a valid URL or not
            validURLRegex = r'^(http:\/\/|https:\/\/|\/\/)[a-z0-9]+([\-\.]{1}[a-z0-9]+)*\.[a-z]{2,5}(:[0-9]{1,5})?(\/.*)?$'
            # Regex for few of the widely used video hosting services
            ytRegex = r'^(?:(?:https?:)?\/\/)?(?:www\.)?(?:youtu\.be\/|youtube(-nocookie)?\.com\/(?:embed\/|v\/|watch\?v=|watch\?.+&v=))((?:\w|-){11})(?:\S+)?$'
            vimeoRegex = r'\/\/(player.)?vimeo.com\/([a-z]*\/)*([0-9]{6,11})[?]?.*'
            dmRegex = r'.+dailymotion.com\/(video|hub|embed)\/([^_]+)[^#]*(#video=([^_&]+))?'
            igRegex = r'(.*)instagram.com\/p\/(.[a-zA-Z0-9]*)'
            ykuRegex = r'(.*).youku\.com\/(v_show\/id_|embed\/)(.+)'

            if not re.search(validURLRegex, video_url):
                return False
            else:
                embedUrl = False
                ytMatch = re.search(ytRegex, video_url)
                vimeoMatch = re.search(vimeoRegex, video_url)
                dmMatch = re.search(dmRegex, video_url)
                igMatch = re.search(igRegex, video_url)
                ykuMatch = re.search(ykuRegex, video_url)

                if ytMatch and len(ytMatch.groups()[1]) == 11:
                    embedUrl = '//www.youtube%s.com/embed/%s?rel=0' % (ytMatch.groups()[0] or '', ytMatch.groups()[1])
                elif vimeoMatch:
                    embedUrl = '//player.vimeo.com/video/%s' % (vimeoMatch.groups()[2])
                elif dmMatch:
                    embedUrl = '//www.dailymotion.com/embed/video/%s' % (dmMatch.groups()[1])
                elif igMatch:
                    embedUrl = '//www.instagram.com/p/%s/embed/' % (igMatch.groups()[1])
                elif ykuMatch:
                    ykuLink = ykuMatch.groups()[2]
                    if '.html?' in ykuLink:
                        ykuLink = ykuLink.split('.html?')[0]
                    embedUrl = '//player.youku.com/embed/%s' % (ykuLink)
                else:
                    # We directly use the provided URL as it is
                    embedUrl = video_url
                return '<iframe class="embed-responsive-item" src="%s" allowFullScreen="true" frameborder="0"></iframe>' % embedUrl

        def static_method(testimonial_ids):
            html_view_static = ''
            for each in testimonial_ids:
                img_url = '/web/image?model=testimonial&id=%s&field=image_av' % (each.id) \
                    if each.image_av else '/ppts_website_theme/static/src/img/profile-empty-round.png'
                html_view_static += """
                            <div class="testomonial-list-card">
                                <div class="userprofiletesto">
                                    <img src="%s" />
                                    <h5>%s</h5>
                                </div>
                                <div>
                                    <h3>%s</h3>
                                    <p>%s</p>
                                </div>
                            </div>
                            """ % (img_url, each.partner_id.name or '', each.name or '', each.description or '')
                if each.video_url != '':
                    if get_video_embed_code(each.video_url):
                        html_view_static += """
                                            <div class="testomonial-videocard">
                                                <div class="row">
                                                    <div class="col-lg-6 col-xl-4  col-md-6 col-sm-12 col-xs-12 testomonial-listcard">
                                                        <div class="testomonial-imgvideo">
                                                            %s
                                                        </div>

                                                        <h4>%s</h4>
                                                    </div>
                                                    
                                        """% (get_video_embed_code(each.video_url), each.name or '')
                return html_view_static
        if int(post['tag_id']) == 0:  # ALL - TAB
            html_view = '<div class="tab-pane fade show active" id="tabA">'
            if post['employee_type'] != 'all' and post['service_type'] != 'all':
                testimonial_ids = request.env['testimonial'].sudo().search([('website_publish', '=', True), ('employee_type','=', int(post['employee_type'])), ('service_type','=', int(post['service_type']))])
            elif post['employee_type'] == 'all' and post['service_type'] != 'all':
                testimonial_ids = request.env['testimonial'].sudo().search([('website_publish', '=', True), ('service_type','=', int(post['service_type']))])
            elif post['employee_type'] != 'all' and post['service_type'] == 'all':
                testimonial_ids = request.env['testimonial'].sudo().search([('website_publish', '=', True), ('employee_type','=', int(post['employee_type']))])
            else:
                testimonial_ids = request.env['testimonial'].sudo().search([('website_publish', '=', True)])
            for each_t in testimonial_ids:
                data = static_method(each_t)
                html_view += '' if data == None else data
            html_view += '</div>'

        if int(post['tag_id']) != 0:  # #OTHER - TAB
            if post['employee_type'] != 'all' and post['service_type'] != 'all':
                next_tab_ids = request.env['testimonial'].sudo().search([('website_publish', '=', True), ('employee_type','=', int(post['employee_type'])), ('service_type','=', int(post['service_type'])),('tags_ids', 'in', int(post['tag_id']))])
            elif post['employee_type'] == 'all' and post['service_type'] != 'all':
                next_tab_ids = request.env['testimonial'].sudo().search([('website_publish', '=', True), ('service_type','=', int(post['service_type'])),('tags_ids', 'in', int(post['tag_id']))])
            elif post['employee_type'] != 'all' and post['service_type'] == 'all':
                next_tab_ids = request.env['testimonial'].sudo().search([('website_publish', '=', True), ('employee_type','=', int(post['employee_type'])),('tags_ids', 'in', int(post['tag_id']))])
            else:
                next_tab_ids = request.env['testimonial'].sudo().search([('website_publish', '=', True),('tags_ids', 'in', int(post['tag_id']))])
            html_view += '<div class="tab-pane fade show active" id="%s">' % ('E' + str(post['tag_id']))
            for each_test in next_tab_ids:
                data = static_method(each_test)
                html_view += '' if data == None else data
            html_view += '</div>'
        return html_view


    
    @http.route(['/press_media'], type='http', auth="public", website=True)
    def theme_press_media(self, **post):
        return request.render('ppts_website_theme.press_and_media_page')

    @http.route(['/search'], type='http', auth="public", website=True)
    def theme_search(self, **post):
        return request.render('ppts_website_theme.theme_search_page')

    @http.route(['/search/result'], type='http', methods=['POST','GET'], auth="public", website=True, csrf=False)
    def theme_search_result(self, **kwargs):
        if kwargs:
            blog_ids = request.env['blog.post'].sudo().search(['|',('name', 'ilike', kwargs['searchinput']),('subtitle', 'ilike', kwargs['searchinput'])])
            blog_vals = []
            for each_blog in blog_ids:
                blog_tag =""
                for each_tag in each_blog.tag_ids:
                    blog_tag = each_tag.name + " " + blog_tag
                blog_vals.append({
                    'image': '/web/image?model=blog.post&id=%s&field=image_av' % (each_blog.id) if each_blog.image_av else '/ppts_website_theme/static/src/img/rc1.jpg',
                    'id':each_blog.id,
                    'idt':each_blog,
                    'name':each_blog.name,
                    'blog_tag_ids': each_blog.tag_ids.ids,
                    'subtitle':each_blog.subtitle,
                    'author_id':each_blog.author_id.name,
                    'visits':each_blog.visits,
                    'date':each_blog.create_date.strftime("%d.%m.%Y"),
                })

            service_ids = request.env['appointment.category'].sudo().search([('name', 'ilike', kwargs['searchinput'])])
            service_vals = []
            for each_service in service_ids:
                service_vals.append({
                    'image': '/web/image?model=appointment.category&id=%s&field=image' % (each_service.id) if each_service.image else '/ppts_website_theme/static/src/img/rc1.jpg',
                    'id':each_service.id,
                    'idt':each_service,
                    'name':each_service.name,
                })

            
            event_ids = request.env['event.event'].sudo().search([('name', 'ilike', kwargs['searchinput'])])
            event_vals=[]
            for i in event_ids:
                book_btn = """ 
                        <a class="borderedbtn" style="color: #00AEC7 !important;" href="#book_free_apt_snippet">Enquire Now</a>
                        <a class="fullbutton" id="selected-event-ID" data-event-id="%s" > Book Now </a>
                    """ % ( i.id )
                event_reg = request.env['event.registration'].search([('event_id','=',i.id)])
                if i.seats_limited == True and i.seats_max <= len(event_reg.ids):
                    book_btn = """ 
                        <a class="borderedbtn" style="color: #00AEC7 !important;" onclick="eventJoinWaitingList(%s)">Join Waiting List</a>
                        <a class="fullbutton event-fully-booked-calendar" onclick="eventAllBookedModal(%s)"> All Booked </a>
                    """ % (str(i.id), str(i.id))

                for t in i.multi_date_line_ids:
                    event_vals.append({
                        'name': i.name or '',
                        'image': '/web/image?model=event.event&amp;id=%s&amp;field=image' % (i.id) if  i.image else '/ppts_website_theme/static/src/img/uc1.jpg',
                        'date': t.date_begin.strftime("%d %B") or '',
                        'time': t.hour_time_begin+':'+t.min_time_begin +' To '+ t.hour_time_end+':'+t.min_time_end or '',
                        'location': i.company_id.name or '',
                        'location_id': i.company_id.id,
                        'event_category_id': i.event_type_id.id,
                        'service_category_id': i.event_service_categ_id.id,
                        'facilitator': i.get_facilitator_name(),
                        'platform': dict(i._fields['type_event'].selection).get(i.type_event),
                        'event_category': i.event_type_id.name or 'NO',
                        'event_sub_categ_id': i.event_sub_categ_id.name or 'NO',
                        'price': i.get_event_price(),
                        'sale_person_id':i.sale_incharge_id.name,
                        'id':i,
                        'book_btn': book_btn,
                        'facilitator_id': i.facilitator_evnt_ids[0].id
                    })

            employee_ids = request.env['hr.employee'].sudo().search([('name', 'ilike', kwargs['searchinput'])])
            employee_vals =[]
            for each_employee in employee_ids:
                job =""
                for each_name in each_employee.employee_type:
                    job = each_name.name + "/" + job
                employee_vals.append({
                        'image':'/web/image?model=hr.employee&id=%s&field=image_1920' % (each_employee.id),
                        'id':each_employee.id,
                        'ide':each_employee,
                        'name':each_employee.name,
                        'job':each_employee.employee_type[0].name or '',
                        'location':each_employee.address_id.name,
                })


            values = {
                'blog_data': blog_vals,
                'search_result': kwargs['searchinput'],
                'service_data':service_vals,
                'employee_data':employee_vals,
                'event_data':event_vals,
            }

            return request.render('ppts_website_theme.theme_search_page_result', values)
        else:
            return request.render('ppts_website_theme.theme_search_page')

    @http.route(['/student'], type='http', auth="public", website=True)
    def student(self, **post):
        return request.render('ppts_website_theme.student_page')

    @http.route(['/healing'], type='http', auth="public", website=True)
    def holistic_healing_page(self, **post):
        return request.render('ppts_website_theme.holistichealing_page')

    @http.route(['/website/parking/details/<int:company_id>'], type='http', auth="public", website=True)
    def website_parking_details(self, company_id ,**post):
        company = request.env['res.company'].sudo().browse(company_id)
        values = {
            'comapny_id': company,
            }
        return request.render('ppts_website_theme.illuminations_parking_details',values)

    @http.route(['/terms/condition/<company_id>'], type='http', auth="public", website=True)
    def website_illuminations_terms_condition_details(self, company_id ,**post):
        _, company_id = unslug(company_id)
        company = request.env['res.company'].sudo().browse(company_id)
        values = {
            'comapny_id': company,
            }
        return request.render('ppts_website_theme.illuminations_terms_condition_details',values)

    @http.route(['/privacy/policy/<company_id>'], type='http', auth="public", website=True)
    def website_illuminations_privacy_policy_details(self, company_id ,**post):
        _, company_id = unslug(company_id) 
        company = request.env['res.company'].sudo().browse(company_id)
        values = {
            'comapny_id': company,
            }
        return request.render('ppts_website_theme.illuminations_privacy_policy_details',values)

    @http.route(['''/healing/<model("calendar.appointment.type"):sub_id>/register'''], type='http', auth="public", website=True)
    def website_appointment_sub_categ(self, sub_id ,**post):
        values = {
            'sub_id': sub_id,
            }
        return request.render('ppts_website_theme.healing_apprpage_page',values)

    @http.route(['''/therapy/<model("calendar.appointment.type"):sub_id>/register'''], type='http', auth="public", website=True)
    def website_appointment_sub_categ_therapy(self, sub_id ,**post):
        # company = request.env['res.company'].sudo().browse(sub_id)
        values = {
            'sub_id': sub_id,
            }
        return request.render('ppts_website_theme.website_therapy_category_page',values)

    @http.route(['/get/model/recruitment/management'], type='http', auth="public", website=True, csrf=False)
    def get_model_recruitment_management(self, **post):
        if post and 'job_id' in post:
            job_id = request.env['hr.job'].sudo().browse(int(post['job_id']))
            type = str(post['type']) if 'type' in post else 'all'
            if type == 'career_therapist':  # CAREER
                if str(post['tab']) == 'Others':
                    next_jobs = request.env['hr.job'].sudo().search(
                        [('website_publish', '=', True), ('company_id.partner_id', '=', int(post['address_id'])),
                         ('state', '=', 'recruit'), ('id', '>', job_id.id),
                         ('department_id.career_type', '=', 'therapist')], limit=1, order='id asc')
                    if len(next_jobs) == 0:
                        next_job_id = request.env['hr.job'].sudo().search(
                            [('website_publish', '=', True), ('company_id.partner_id', '=', int(post['address_id'])),
                             ('state', '=', 'recruit'), ('department_id.career_type', '=', 'therapist')], limit=1,
                            order='id asc')
                    else:
                        next_job_id = next_jobs
                else:
                    next_jobs = request.env['hr.job'].sudo().search(
                        [('website_publish', '=', True), ('state', '=', 'recruit'), ('id', '>', job_id.id),
                         ('department_id.career_type', '=', 'therapist')], limit=1, order='id asc')
                    if len(next_jobs) == 0:
                        next_job_id = request.env['hr.job'].sudo().search(
                            [('website_publish', '=', True), ('state', '=', 'recruit'),
                             ('department_id.career_type', '=', 'therapist')], limit=1, order='id asc')
                    else:
                        next_job_id = next_jobs
            else:  # ALL
                next_jobs = request.env['hr.job'].sudo().search(
                    [('website_publish', '=', True), ('state', '=', 'recruit'), ('id', '>', job_id.id),
                     ('department_id.career_type', '=', 'therapist')], limit=1, order='id asc')
                if len(next_jobs) == 0:
                    next_job_id = request.env['hr.job'].sudo().search(
                        [('website_publish', '=', True), ('state', '=', 'recruit'),
                         ('department_id.career_type', '=', 'therapist')], limit=1,
                        order='id asc')  # remove department_id after therapist page done
                else:
                    next_job_id = next_jobs
            if next_job_id != False:
                if int(post['job_id']) == next_job_id.id:
                    final_job_id = False
                else:
                    final_job_id = next_job_id.id
            else:
                final_job_id = False
            responsibilities = []
            qualifications = []
            for i in job_id.responsibilities: responsibilities.append(i.name)
            for i in job_id.qualifications: qualifications.append(i.name)
            av = {
                'title': job_id.name, 'description': job_id.description or '',
                'responsibilities': responsibilities, 'qualifications': qualifications,
                'next_job': final_job_id}
            return json.dumps(av)

    @http.route(['/get/model/student/data'], type='http', auth="public", website=True, csrf=False)
    def get_model_student_data(self, **post):
        if post and 'emp_id' in post:
            emp_id = request.env['hr.employee'].sudo().browse(int(post['emp_id']))
            certifications = []
            next_emp = request.env['hr.employee'].sudo().search([('id', '>', emp_id.id),('is_student','=',True)], limit=1, order='id asc')
            if len(next_emp) == 0:
                next_emp_id = request.env['hr.employee'].sudo().search([('is_student','=',True)], limit=1, order='id asc')
            else:
                next_emp_id = next_emp
            if next_emp_id != False:
                if int(post['emp_id']) == next_emp_id.id:
                    final_emp_id = False
                else:
                    final_emp_id = next_emp_id.id
            else:
                final_emp_id = False
            for i in emp_id.certification_ids: certifications.append(i.certificate_id.name)
            data = {
                'title': emp_id.name, 'about': emp_id.about_employee or '',
                'image': '/web/image?model=hr.employee&id=%s&field=image_1920' % (emp_id.id) if emp_id.image_1920 else '/web/image?model=hr.employee&id=%s&field=image_128',
                'certifications': certifications,
                'next_emp': final_emp_id}
            return json.dumps(data)

    @http.route(['/get/event/filter/popular/<string:location>'], type='http', auth="public", methods=['GET'], website=True, csrf=False)
    def get_event_filter(self, **kwargs):
        values = dict(kwargs)
        data = {}
        html = ''
        location_ids = str(values['location']).strip('][').split(',')
        if location_ids != ['']:
            for location_id in range(0, len(location_ids)):
                location_ids[location_id] = int(location_ids[location_id])
        else:
            location_ids = []
        if location_ids != []:
            event_ids = request.env['event.event'].sudo().search([('stage_id', 'in', ('Published', 'Announced')), ('company_id', 'in' ,location_ids)], order='seats_expected desc')
        else:
            event_ids = request.env['event.event'].sudo().search([('stage_id', 'in', ('Published', 'Announced'))], limit=3, order='seats_expected desc')
        if event_ids:
            for event_id in event_ids:
                if event_id.multi_date_line_ids:
                    multi_date_line = request.env['multi.date.line'].sudo().search([('event_id','=',event_id.id)],limit=1)
                    event_time = str(multi_date_line.hour_time_begin) + ':'+ str(multi_date_line.min_time_begin) + '-'+ str(multi_date_line.hour_time_end) + ':'+ str(multi_date_line.min_time_end)
                type_event = dict(event_id._fields['type_event'].selection).get(event_id.type_event)
                if event_id.s_start_date:
                    date = str(event_id.s_start_date.day) + ' ' +str(calendar.month_name[event_id.s_start_date.month])
                else:
                    if event_id.event_start and event_id.event_end:
                        date = str(event_id.event_start) + ' To ' +  str(event_id.event_end)
                    else:
                        date = ''
                html += """
                <div class="col-xl-4 col-lg-6 col-md-6 col-sm-12 col-xs-12">
                    <div class="calenday-eventlist-item column-wisecard-listcontainer">
                        <div class="cal-event-img"><label class="filtercatlabel">%s</label><img src="/ppts_website_theme/static/src/img/mstp1.jpg" /></div>
                        <div class="eventfullinfos">
                            <div class="event-typoingo">
                                <div class="eventtitleinfos">
                                    <div style="width: -webkit-fill-available;"><label class="training chipsone">%s</label></div>
                                    <h5 class="l-event-h5-2line-elipsis"><a class="a-clr" href="/event/%s/register" data-toggle="tooltip" data-placement="top" title="%s">%s</a></h5>
                                </div>
                                <div class="eventinfos">
                                    <label><i class="fas fa-map-marker-alt"></i> %s</label>
                                    <label><i class="far fa-calendar-minus"></i> %s</label>
                                    <label><i class="far fa-clock"></i> %s</label>
                                    <label data-toggle="tooltip" data-placement="top" title="%s" class="evt-card-rw-label"><i class="far fa-user"></i> %s</label>
                                </div>
                            </div>
                            <div class="event-listbtn"><a href="/contactus" class="borderedbtn" style="min-width: 140px;width: %s;">Enquire Now</a><a href="/contactus" class="fullbutton" style="min-width: 140px;width: %s;">Book Now </a></div>
                        </div>
                    </div>
                </div>
            """ %(type_event or '', event_id.event_type_id.name or '', slug(event_id), event_id.name or '',
                  event_id.name or '', event_id.company_id.name or '',  date,
                       str(event_time),
                  event_id.get_facilitator_name(), event_id.get_facilitator_name(),"""100%""", """100%""")
        
        else:
            html += '<div class="col-12 text-center" style="min-height:300px"><h3>No Events</h3></div>'

        data['data'] = html
        return json.dumps(data)

    @http.route(['/get/model/holistic-healing/filter/<string:type>/<string:Cat>/<string:Sub>/<string:Tag>'], type='http', auth="public", methods=['GET'], website=True, csrf=False)
    def get_model_healing_filter(self, **kwargs):
        def static_html(img_url, name):
            value_html = """<div class="col-xs-4 col-lg-4 col-md-6 col-sm-6 col-xs-12 service-lists-items-wrapper">
                                <div class="service-lists-item">
                                    <img src="%s" alt="serviceimageone" loading="lazy" />
                                    <div class="service-svg-shapes-overlay">
                                        <div class="wrapper">
                                            <div class="side_side"> </div>
                                        </div>
                                        <h4>%s</h4>
                                    </div>
                                </div>
                            </div>
                            """ %(img_url, name)
            return value_html

        def static_function(onclick, img_url1, name1,categ_id):
            value_html1 = """<div class="col-xs-4 col-lg-4 col-md-6 col-sm-6 col-xs-12 service-lists-items-wrapper" onclick="%s">
                                <div class="service-lists-item">
                                    <img src="%s" alt="serviceimageone" loading="lazy"  />
                                    <div class="service-svg-shapes-overlay">
                                        <div class="wrapper">
                                            <div class="side_side"> </div>
                                        </div>
                                        <h4>%s</h4>
                                        <a href="%s">
                                        </a>                                        
                                    </div>
                                </div>
                                
                            </div>
                            
                            """ %(onclick, img_url1, name1,categ_id)
            return value_html1
        values = dict(kwargs)
        data = {}
        tag_ids = str(values['Tag']).strip('][').split(',')
        if tag_ids != ['']:
            for tag in range(0, len(tag_ids)):
                tag_ids[tag] = int(tag_ids[tag])
        else:
            tag_ids = []
        if values['type'] == 'tag':
            html_view = ''
            if str(values['Cat']) != 'all' and str(values['Sub']) != 'all' and tag_ids != []:
                category_ids = request.env['calendar.appointment.type'].sudo().search([('website_publish', '=', True), ('service_categ_id', '=', int(values['Cat'])), ('id', '=', int(values['Sub'])), ('tag_ids', 'in', tag_ids)], order='id asc')
                for each in category_ids:
                    img_url = '/web/image?model=calendar.appointment.type&id=%s&field=image' % (each.id) \
                        if each.image else '/ppts_website_theme/static/src/img/hs6.jpg'
                    html_view += static_function("HealingSubDiv(%s)" % each.id, img_url, each.name)
            elif str(values['Cat']) == 'all' and str(values['Sub']) == 'all' and tag_ids != []:
                category_ids = request.env['appointment.category'].sudo().search([('website_publish', '=', True), ('tag_ids', 'in', tag_ids)], order='id asc')
                for each in category_ids:
                    img_url = '/web/image?model=appointment.category&id=%s&field=image' % (each.id) \
                        if each.image else '/ppts_website_theme/static/src/img/hs6.jpg'
                    html_view += static_function("HealingCatDiv(%s, 'category')"% each.id, img_url, each.name)
                html_view += static_html("/ppts_website_theme/static/src/img/hs6.jpg", "Free Wellness Consultation")
            elif str(values['Cat']) == 'all' and str(values['Sub']) != 'all' and tag_ids != []:
                category_ids = request.env['appointment.category'].sudo().search([('website_publish', '=', True), ('id', '=', int(values['Sub'])), ('tag_ids', 'in', tag_ids)], order='id asc')
                for each in category_ids:
                    img_url = '/web/image?model=appointment.category&id=%s&field=image' % (each.id) \
                        if each.image else '/ppts_website_theme/static/src/img/hs6.jpg'
                    html_view += static_function("HealingCatDiv(%s, 'category')"% each.id, img_url, each.name)
                html_view += static_html("/ppts_website_theme/static/src/img/hs6.jpg", "Free Wellness Consultation")
            elif str(values['Cat']) != 'all' and str(values['Sub']) == 'all' and tag_ids != []:
                category_ids = request.env['calendar.appointment.type'].sudo().search([('website_publish', '=', True), ('service_categ_id', '=', int(values['Cat'])), ('tag_ids', 'in', tag_ids)], order='id asc')
                for each in category_ids:
                    img_url = '/web/image?model=calendar.appointment.type&id=%s&field=image' % (each.id) \
                        if each.image else '/ppts_website_theme/static/src/img/hs6.jpg'
                    html_view += static_function("HealingSubDiv(%s)" % each.id, img_url, each.name,each.website_url)
            elif str(values['Cat']) != 'all' and str(values['Sub']) == 'all' and tag_ids == []:
                category_ids = request.env['calendar.appointment.type'].sudo().search([('website_publish', '=', True), ('service_categ_id', '=', int(values['Cat']))], order='id asc')
                for each in category_ids:
                    img_url = '/web/image?model=calendar.appointment.type&id=%s&field=image' % (each.id) \
                        if each.image else '/ppts_website_theme/static/src/img/hs6.jpg'
                    html_view += static_function("HealingSubDiv(%s)" % each.id, img_url, each.name, each.website_url)
            elif str(values['Cat']) == 'all' and str(values['Sub']) != 'all' and tag_ids == []:
                category_ids = request.env['appointment.category'].sudo().search([('website_publish', '=', True), ('id', '=', int(values['Sub']))], order='id asc')
                for each in category_ids:
                    img_url = '/web/image?model=appointment.category&id=%s&field=image' % (each.id) \
                        if each.image else '/ppts_website_theme/static/src/img/hs6.jpg'
                    html_view += static_function("HealingCatDiv(%s, 'category')"% each.id, img_url, each.name,)
                html_view += static_html("/ppts_website_theme/static/src/img/hs6.jpg", "Free Wellness Consultation")
            elif str(values['Cat']) != 'all' and str(values['Sub']) != 'all' and tag_ids == []:
                category_ids = request.env['calendar.appointment.type'].sudo().search([('website_publish', '=', True), ('service_categ_id', '=', int(values['Cat'])), ('id', '=', int(values['Sub']))], order='id asc')
                for each in category_ids:
                    img_url = '/web/image?model=calendar.appointment.type&id=%s&field=image' % (each.id) \
                        if each.image else '/ppts_website_theme/static/src/img/hs6.jpg'
                    html_view += static_function("HealingSubDiv(%s)" % each.id, img_url, each.name,each.website_url)
            else:
                category_ids = request.env['appointment.category'].sudo().search([('website_publish', '=', True)], order='id asc')
                for each in category_ids:
                    img_url = '/web/image?model=appointment.category&id=%s&field=image' % (each.id) \
                        if each.image else '/ppts_website_theme/static/src/img/hs6.jpg'
                    html_view += static_function("HealingCatDiv(%s, 'category')"% each.id, img_url, each.name,each)
                html_view += static_html("/ppts_website_theme/static/src/img/hs6.jpg", "Free Wellness Consultation")

            data = {'data': html_view}
        elif values['type'] == 'category':
            html = ''
            if str(values['Cat']) == 'all':
                if tag_ids != []:
                    category_ids = request.env['appointment.category'].sudo().search([('website_publish', '=', True), ('tag_ids', 'in', tag_ids)], order='id asc')
                else:
                    category_ids = request.env['appointment.category'].sudo().search([('website_publish', '=', True),('category_type','=','healing')], order='id asc')
                        
                filter_view = '<option value="all" selected="selected">Choose Your Sub Category</option>'
                vals = ''
                for i in category_ids:
                    img_url = '/web/image?model=appointment.category&id=%s&field=image' % (i.id) \
                        if i.image else '/ppts_website_theme/static/src/img/hs6.jpg'
                    
                    html += static_function("HealingCatDiv(%s, 'category')"% i.id, img_url, i.name,vals)
                html += static_html("/ppts_website_theme/static/src/img/hs6.jpg", "Free Wellness Consultation")
            else:
                if tag_ids != []:
                    category_ids = request.env['calendar.appointment.type'].sudo().search(
                        [('website_publish', '=', True), ('service_categ_id', '=', int(values['Cat'])), ('tag_ids', 'in', tag_ids)], order='id asc')
                else:
                    category_ids = request.env['calendar.appointment.type'].sudo().search(
                        [('website_publish', '=', True), ('service_categ_id', '=', int(values['Cat']))], order='id asc')
                filter_view = '<option value="all" selected="selected">Choose Your Sub Category</option>'
                for i in category_ids:
                    filter_view += """<option  id="%s" value="%s">%s</option>"""%(i.id, i.id, i.name)
                    img_url = '/web/image?model=calendar.appointment.type&id=%s&field=image' % (i.id) \
                        if i.image else '/ppts_website_theme/static/src/img/hs6.jpg'
                    html += static_function("HealingSubDiv(%s)" % i.id, img_url, i.name,i.website_url)
            data = {'sub_cat': html, 'filter': filter_view,}
        elif values['type'] == 'sub':
            html = ''
            if str(values['Sub']) == 'all':
                if tag_ids != []:
                    category_ids = request.env['calendar.appointment.type'].sudo().search([('website_publish', '=', True), ('tag_ids', 'in', tag_ids)], order='id asc')
                else:
                    if str(values['Cat']) != 'all' and str(values['Sub']) == 'all' and tag_ids == []:
                        category_ids = request.env['calendar.appointment.type'].sudo().search([('website_publish', '=', True), ('service_categ_id', '=', int(values['Cat']))], order='id asc')
                    # category_ids = request.env['calendar.appointment.type'].sudo().search([('website_publish', '=', True), ('tag_ids', 'in', tag_ids)], order='id asc')
                for i in category_ids:
                    img_url = '/web/image?model=calendar.appointment.type&id=%s&field=image' % (i.id) \
                        if i.image else '/ppts_website_theme/static/src/img/hs6.jpg'
                    html += static_function("HealingSubDiv(%s)" % i.id, img_url, i.name,i.website_url)
            else:
                if tag_ids != []:
                    category_ids = request.env['calendar.appointment.type'].sudo().search([('id', '=', int(values['Sub'])), ('tag_ids', 'in', tag_ids)])
                else:
                    category_ids = request.env['calendar.appointment.type'].sudo().browse(int(values['Sub']))
                for i in category_ids:
                    img_url = '/web/image?model=calendar.appointment.type&id=%s&field=image' % (i.id) \
                        if i.image else '/ppts_website_theme/static/src/img/hs6.jpg'
                    html += static_function("HealingSubDiv(%s)" % i.id, img_url, i.name,i.website_url)

            data = {'sub_cat': html}
        return json.dumps(data)

    @http.route(['/get/model/holistic-healing/<string:type>/<string:Cat>'], type='http', auth="public", methods=['GET'], website=True, csrf=False)
    def get_model_healing_data(self, **kwargs):
        option = '<option value="all" selected="selected">Select a Sub Service</option>'
        values = dict(kwargs)
        if str(kwargs['Cat']) == 'all':
            option += ''
        else:
            sub_cat_ids = request.env['calendar.appointment.type'].sudo().search([('website_publish', '=', True), ('service_categ_id', '=', int(values['Cat']))], order='id asc')
            for each in sub_cat_ids:
                option += """<option value="%s">%s</option>""" % (each.id, each.name)
        data = {'data': option}
        return json.dumps(data)

    @http.route(['/healing-approaches/<string:id>'], type='http', auth="public", methods=['GET'], website=True, csrf=False)
    def healing_approaches(self, **kwargs):
        values = dict(kwargs)
        sub_cat = request.env['calendar.appointment.type'].sudo().browse(int(values['id']))
        img_url = '/web/image?model=calendar.appointment.type&id=%s&field=image' % (sub_cat.id) \
            if sub_cat.sudo().image else '/ppts_website_theme/static/src/img/healingappro_banner.jpg'
        healing = []
        for each in sub_cat.healing_content_ids:
            arry = {'id': each.id,'title': each.healing_id.name, 'content': each.html}
            healing.append(arry)
        event_ids = request.env['event.event'].sudo().search([('event_sub_categ_id', '=', sub_cat.id)], order='id asc')
        html = ''
        for event in event_ids:
            if event.type_event == 'type_online':
                type_event = 'Online'
            elif event.type_event == 'type_onsite':
                type_event = 'Onsite'
            else:
                type_event = 'Hybrid'
            image_url = '/web/image?model=event.event&id=%s&field=image' % (event.id) \
                if event.image else '/ppts_website_theme/static/src/img/ue2.jpg'
            html += """<div class="calenday-eventlist-item aos-init aos-animate" data-aos="fade-up" data-aos-delay="600">
                                <div class="cal-event-img">
                                    <label class="filtercatlabel">%s</label>
                                    <img src="%s"/>
                                    <div class="eventtag-imgoverlay chips-cont">
                                        <label class="training chipsone other-chips">%s</label>
                                    </div>
                                </div>
                                <div class="eventfullinfos">
                                    <div class="event-typoingo">
                                        <div class="eventtitleinfos">
                                            <h5 class="l-event-h5-2line-elipsis">
                                                <a class="a-clr" href="/event/%s/register" data-toggle="tooltip" data-placement="top" title="%s">
                                                    %s
                                                </a>
                                            </h5>
                                        </div>
                                        <div class="eventinfos">
                                            <label><i class="fas fa-map-marker-alt"></i> %s</label>
                                            <label><i class="far fa-calendar-minus"></i> %s</label>
                                            <label><i class="far fa-clock"></i> %s</label>
                                            <label><i class="far fa-user"></i> %s</label>
                                        </div>
                                    </div>
                                    <div class="event-listbtn">
                                        <a href="/contactus" class="borderedbtn">Enquire Now</a>
                                        <a href="/contactus" class="fullbutton">Book Now</a>
                                    </div>
                                </div>
                            </div>
                        
                    """ % (type_event or '', image_url, event.event_type_id.name or '', slug(event), event.name, event.name,
                           event.address_id.name or '', event.s_start_date,
                       str(event.get_start_end_time()),
                           event.user_id.name or '')
        data = {'link': "<a href='/healing/%s/register'>%s</a>" % (sub_cat.id, sub_cat.name), 'sub_cat': """<input type="hidden" value="%s" name="subCategoryId" id="subCategoryId"/>"""%(sub_cat.id),
                'name': sub_cat.name, 'description': sub_cat.description, 'image': img_url, 'healing_questions': healing, 'event': html}
        # return request.render('ppts_website_theme.healing_approaches_page', data)
        return request.render('ppts_website_theme.holistichealing_page', data)

    @http.route(['/get/model/healing-approaches/data'], type='http', auth="public", website=True, csrf=False)
    def get_model_healing_approaches_data(self, **post):
        sub_cat_id = post['sub_cat_id']
        if str(post['type']) == 'all':
            event_ids = request.env['event.event'].sudo().search([('event_sub_categ_id', '=', int(sub_cat_id))], order='id asc')
        else:
            if str(post['type']) == 'online':
                type_event = 'type_online'
            elif str(post['type']) == 'onsite':
                type_event = 'type_onsite'
            else:
                type_event = 'type_hybrid'
            event_ids = request.env['event.event'].sudo().search([('event_sub_categ_id', '=', int(sub_cat_id)),('type_event', '=', type_event)], order='id asc')
        html = ''
        for event in event_ids:
            if event.type_event == 'type_online':
                type = 'Online'
            elif event.type_event == 'type_onsite':
                type = 'Onsite'
            else:
                type = 'Hybrid'
            image_url = '/web/image?model=event.event&id=%s&field=image' % (event.id) \
                if event.image else '/ppts_website_theme/static/src/img/ue2.jpg'
            html += """<div class="calenday-eventlist-item aos-init aos-animate" data-aos="fade-up" data-aos-delay="600">
                        <div class="cal-event-img">
                            <label class="filtercatlabel">%s</label>
                            <img src="%s"/>
                            <div class="eventtag-imgoverlay chips-cont">
                                <label class="training chipsone other-chips">%s</label>
                            </div>
                        </div>
                        <div class="eventfullinfos">
                            <div class="event-typoingo">
                                <div class="eventtitleinfos">
                                    <h5>%s</h5>
                                </div>
                                <div class="eventinfos">
                                    <label><i class="fas fa-map-marker-alt"></i> %s</label>
                                    <label><i class="far fa-calendar-minus"></i> %s</label>
                                    <label><i class="far fa-clock"></i> %s</label>
                                    <label><i class="far fa-user"></i> %s</label>
                                </div>
                            </div>
                            <div class="event-listbtn">
                                <a href="/contactus" class="borderedbtn">Enquire Now</a>
                                <a href="/contactus" class="fullbutton">Book Now</a>
                            </div>
                        </div>
                    </div>
                """ % (type or '', image_url, event.event_type_id.name or '', event.name,
                       event.address_id.name or '', event.s_start_date,
                       str(event.get_start_end_time()),
                       event.user_id.name or '')
        return html

    @http.route(['/initial-application-form/<string:job_id>'], type='http', auth="public", website=True)
    def initial_application_form(self, **post):
        return request.render('ppts_website_theme.initial_application_form_page', {'job_id':  post['job_id']})

    @http.route(['/management-application-form/<string:job_id>'], type='http', auth="public", website=True)
    def management_application_form(self, **post):
        return request.render('ppts_website_theme.management_application_form_page', {'job_id':  post['job_id']})

    @http.route(['/website/initial-application-form'], type='http', auth="public", website=True)
    def initial_application_page(self, **post):
        return request.render('ppts_website_theme.initial_application_form_page')   

    @http.route(['/initial-application-form/category'], type='http', auth="public", methods=['GET'], website=True, csrf=False)
    def initial_application_form_category(self, **kwargs):
        data = []
        sub_cat_ids = request.env['calendar.appointment.type'].sudo().search([('website_publish', '=', True)], order='id asc')
        sorted_orders = sorted(sub_cat_ids, key=lambda o: o.service_categ_id.id)
        for service_categ_id, sub_cat_lst in groupby(sorted_orders, key=lambda o: o.service_categ_id.id):
            categ_id = request.env['appointment.category'].sudo().browse(service_categ_id)
            children = []
            for each in list(sub_cat_lst):
                children.append({"text": each.name, "id": each.id, "parent_id": categ_id.id})
            data.append({"text": categ_id.name, "id": categ_id.id, "children": children})
        data = {'data': data}
        return json.dumps(data)

    @http.route(['/management/application/submit/<int:job_id>'], type='http', methods=['POST'], auth="public", website=True, csrf=False)
    def management_application_submit(self, job_id, **kw):
        job = request.env['hr.job'].sudo().browse(job_id)
        ap_id = request.env['hr.applicant'].sudo().create({
            'job_id': job_id,
            'name': 'Illumination ' + job.name + ' Job Application',
            'email_from': kw['email'],
            'partner_name': str(kw['name']),
            'partner_mobile': kw['contact'] or '',
            'notice_period': kw['notice_period'] or None,
            'work_experience': kw['work_exp'] or None,
            'company_id': int(kw['company_id']) or None,
        })

        if 'resume' in request.params:
            attached_files = request.httprequest.files.getlist('resume')
            for attachment in attached_files:
                if attachment:
                    request.env['ir.attachment'].sudo().create({
                        'name': attachment.filename,
                        'res_model': 'hr.applicant',
                        'res_id': ap_id.id,
                        'type': 'binary',
                        'datas': base64.b64encode(attachment.read()),
                    })

        msg = 'Thanks for submiting the application we will send updates to '+ kw['email']
        return http.request.render("ppts_website_theme.theme_success_page", {"title": 'Your Application Submited SUCCESSFULLY!',"msg":msg})
        
    @http.route(['/initial/application/submit/<int:job_id>'], type='http', methods=['POST'], auth="public", website=True, csrf=False)
    def initial_application_submit(self, job_id, **kw):
        gender = ''
        if 'flexRadioDefaultGender0' in kw:
            gender = str(kw['flexRadioDefaultGender0'])
        elif 'flexRadioDefaultGender1' in kw:
            gender = str(kw['flexRadioDefaultGender1'])
        facilitator = ''
        if 'facilitator0' in kw:
            facilitator = str(kw['facilitator0'])
        elif 'facilitator1' in kw:
            facilitator = str(kw['facilitator1'])
        relocate = ''
        if 'relocate0' in kw:
            relocate = str(kw['relocate0'])
        elif 'relocate1' in kw:
            relocate = str(kw['relocate1'])
        if 'type0' in kw:
            type = str(kw['type0'])
        elif 'type1' in kw:
            type = str(kw['type1'])
        elif 'type2' in kw:
            type = str(kw['type2'])
        else:
            type = ''
        approaches_ids = []
        if 'approaches' in kw:
            approaches = json.loads(kw['approaches'])
            sorted_orders = sorted(approaches, key=lambda o: o['parent_id'])
            for service_categ_id, sub_cat_lst in groupby(sorted_orders, key=lambda o: o['parent_id']):
                categ_id = request.env['appointment.category'].sudo().browse(service_categ_id)
                children = []
                for each in list(sub_cat_lst):
                    children.append(each['data_id'])
                approaches_ids.append((0,0, {'service_category_id': categ_id.id, 'sub_category_id': [(6, 0, children)]}))
        question_answer_ids = []
        if 'question_options' in kw:
            question_options = json.loads(kw['question_options'])
            sorted_que_orders = sorted(question_options, key=lambda o: o['parent_id'])
            for question_id, answer_data in groupby(sorted_que_orders, key=lambda o: o['parent_id']):
                que_id = request.env['initial.application.question'].sudo().browse(question_id)
                answer_list = []
                for each_ans in list(answer_data):
                    answer_list.append(each_ans['data_id'])
                question_answer_ids.append((0, 0, {'question_id': que_id.id, 'answer_id': [(6, 0, answer_list)]}))
        job = request.env['hr.job'].sudo().browse(job_id)
        ap_id = request.env['hr.applicant'].sudo().create({
            'job_id': job_id,
            'name': 'Illumination ' + job.name + ' Job Application',
            'email_from': kw['email'],
            'partner_name': str(kw['name']) + ' ' + str(kw['last_name']),
            'partner_mobile': kw['phone_number[full]'] or '',
            'healer': str(kw['healer']) or '',
            'dob': kw['dob'] or False,
            'gender': gender,
            'approaches_ids': approaches_ids,
            'question_answer_ids': question_answer_ids,
            'facilitator': facilitator,
            'country_id': int(kw['country_id']) or None,
            'url': str(kw['url']) or '',
            'city_id': int(kw['city_id']) or None,
            'relocate': relocate,
            'type': type,
            'others': str(kw['others']) or '',
        })
        if 'app_file' in request.params:
            attached_files = request.httprequest.files.getlist('app_file')
            for attachment in attached_files:
                if attachment:
                    request.env['ir.attachment'].sudo().create({
                        'name': attachment.filename,
                        'res_model': 'hr.applicant',
                        'res_id': ap_id.id,
                        'type': 'binary',
                        'datas': base64.b64encode(attachment.read()),
                    })

        msg = 'Thanks for submiting the application we will send updates to '+ kw['email']
        return http.request.render("ppts_website_theme.theme_success_page", {"title": 'Your Application Submited SUCCESSFULLY!',"msg":msg})

    @http.route(['/get/model/student/filter/<string:StudentLocationList>/<string:hrCertificationList>'], type='http', auth="public", methods=['GET'], website=True, csrf=False)
    def get_model_student_filter(self, **kwargs):
        values = dict(kwargs)
        data = values
        StudentLocationList = str(data['StudentLocationList']).strip('][').split(',')
        if StudentLocationList != ['']:
            for StudentLocation in range(0, len(StudentLocationList)):
                StudentLocationList[StudentLocation] = int(StudentLocationList[StudentLocation])
        else:
            StudentLocationList = []
        hrCertificationList = str(data['hrCertificationList']).strip('][').split(',')
        if hrCertificationList != ['']:
            for hrCertification in range(0, len(hrCertificationList)):
                hrCertificationList[hrCertification] = int(hrCertificationList[hrCertification])
        else:
            hrCertificationList = []
        html = ''
        if StudentLocationList != [] and hrCertificationList != []:
            emp_ids = []
            certification_ids = request.env['certification'].sudo().search([('employee_id.is_student','=',True),('employee_id.address_id', 'in', StudentLocationList),
                                                                ('certificate_id', 'in', hrCertificationList)])
            for i in certification_ids:
                if i.employee_id not in emp_ids:
                    emp_ids.append(i.employee_id)
        elif StudentLocationList == [] and hrCertificationList != []:
            emp_ids = []
            certification_ids = request.env['certification'].sudo().search([('employee_id.is_student', '=', True),
                                                                ('certificate_id', 'in', hrCertificationList)])
            for i in certification_ids:
                if i.employee_id not in emp_ids:
                    emp_ids.append(i.employee_id)
        elif StudentLocationList != [] and hrCertificationList == []:
            emp_ids = request.env['hr.employee'].sudo().search([('is_student', '=', True),
                                                                ('address_id', 'in', StudentLocationList)])
        else:
            emp_ids = request.env['hr.employee'].sudo().search([('is_student', '=', True)])
        if len(emp_ids) != 0:
            for emp_id in emp_ids:
                html += """
                            <div class="col-xl-3 col-lg-4 col-md-6 col-sm-6 col-xs-12" data-aos="fade-up" data-aos-delay="200">
                                <div class="therapest-list-container student-list-detail">
                                    <img  class="student-list-detail-image" src="%s" />
                                    <h5 class="student-list-detail-name">%s</h5>
                                    <p class="student-list-detail-designations">%s</p>
                                    <p class="student-list-detail-button"  onclick="StudentModel(%s)">About Us</p>
                                </div>
                            </div>
                """ %('/web/image?model=hr.employee&id=%s&field=image_1920' % (emp_id.id) if emp_id.image_1920 else '/web/image?model=hr.employee&id=%s&field=image_128',
                      str(emp_id.name) or '', emp_id.get_job_position_website() or '', emp_id.id)
        data = {'html': html}
        return json.dumps(data)

    @http.route(['/career/therapist'], type='http', auth="public", website=True)
    def theme_career_therapist(self, **post):
        values = {}
        all = [];
        location_lst = []
        all_jobs = request.env['hr.job'].sudo().search([('website_publish', '=', True), ('state', '=', 'recruit'),
                                                        ('department_id.career_type', '=', 'therapist')],
                                                       order='id asc')
        for i in all_jobs:
            all.append({
                'id': i.id,
                'title': i.name or ' ',
                'description': i.description or ' ',
                'company_name': i.company_id.name,
                'company_id': i.company_id.id,
                'address_id': i.address_id.id,
                'job_type': dict(i._fields['job_type'].selection).get(i.job_type),
                'no_of_recruitment': i.no_of_recruitment,
                'image_url': '/web/image?model=hr.job&id=%s&field=image_av' % (i.id) \
                    if i.image_av else '/ppts_website_theme/static/src/img/op1.jpg',
                'department_id': i.department_id.career_type,
            })
        location_ids = request.env['res.partner'].sudo().search([('is_job_location', '=', True)])
        for i in location_ids:
            job_ids = request.env['hr.job'].sudo().search(
                [('website_publish', '=', True), ('address_id', '=', i.id), ('state', '=', 'recruit'),
                 ('department_id.career_type', '=', 'therapist')], order='id asc')
            job_lst = []
            for j in job_ids:
                job_lst.append({
                    'id': j.id,
                    'title': j.name or ' ',
                    'description': j.description or ' ',
                    'company_name': j.company_id.name,
                    'company_id': j.company_id.id,
                    'address_id': j.address_id.id,
                    'job_type': dict(j._fields['job_type'].selection).get(j.job_type),
                    'no_of_recruitment': j.no_of_recruitment,
                    'image_url': '/web/image?model=hr.job&id=%s&field=image_av' % (j.id) \
                        if j.image_av else '/ppts_website_theme/static/src/img/op1.jpg',
                    'department_id': j.department_id.career_type,
                })
            location_lst.append({'id': i.id, 'jobs_tab': job_lst})
        values = {'all_jobs': all, 'locations_ids': location_lst}
        return request.render('ppts_website_theme.theme_career_therapist_page', values)

    @http.route(['/career/management'], type='http', auth="public", website=True)
    def theme_career_management(self, **post):
        values = {}
        all = [];
        location_lst = []
        all_jobs = request.env['hr.job'].sudo().search([('website_publish', '=', True), ('state', '=', 'recruit'),
                                                        ('department_id.career_type', '=', 'management')],
                                                       order='id asc')
        for i in all_jobs:
            all.append({
                'id': i.id,
                'title': i.name or ' ',
                'description': i.description or ' ',
                'company_name': i.company_id.name,
                'company_id': i.company_id.id,
                'address_id': i.address_id.id,
                'job_type': dict(i._fields['job_type'].selection).get(i.job_type),
                'no_of_recruitment': i.no_of_recruitment,
                'image_url': '/web/image?model=hr.job&id=%s&field=image_av' % (i.id) \
                    if i.image_av else '/ppts_website_theme/static/src/img/op1.jpg',
                'department_id': i.department_id.career_type,
            })
        location_ids = request.env['res.partner'].sudo().search([('is_job_location', '=', True)])
        for i in location_ids:
            job_ids = request.env['hr.job'].sudo().search(
                [('website_publish', '=', True), ('address_id', '=', i.id), ('state', '=', 'recruit'),
                 ('department_id.career_type', '=', 'management')], order='id asc')
            job_lst = []
            for j in job_ids:
                job_lst.append({
                    'id': j.id,
                    'title': j.name or ' ',
                    'description': j.description or ' ',
                    'company_name': j.company_id.name,
                    'company_id': j.company_id.id,
                    'address_id': j.address_id.id,
                    'job_type': dict(j._fields['job_type'].selection).get(j.job_type),
                    'no_of_recruitment': j.no_of_recruitment,
                    'image_url': '/web/image?model=hr.job&id=%s&field=image_av' % (j.id) \
                        if j.image_av else '/ppts_website_theme/static/src/img/op1.jpg',
                    'department_id': j.department_id.career_type,
                })
            location_lst.append({'id': i.id, 'jobs_tab': job_lst})
        values = {'all_jobs': all, 'each_locations_ids': location_lst}
        return request.render('ppts_website_theme.theme_career_management_page', values)

    @http.route(['/career'], type='http', auth="public", website=True)
    def theme_career(self, **post):
        all = [];
        location_lst = []

        all_jobs = request.env['hr.job'].sudo().search([('website_publish', '=', True)], order='id asc')
        for i in all_jobs:
            all.append({
                'id': i.id,
                'title': i.name or ' ',
                'description': i.description or ' ',
                'company_name': i.company_id.name,
                'company_id': i.company_id.id,
                'address_id': i.address_id.id,
                'job_type': dict(i._fields['job_type'].selection).get(i.job_type),
                'no_of_recruitment': i.no_of_recruitment,
                'image_url': '/web/image?model=hr.job&id=%s&field=image_av' % (i.id) \
                    if i.image_av else '/ppts_website_theme/static/src/img/op1.jpg',
                'department_id': i.department_id.career_type,
            })

        location_ids = request.env['res.partner'].sudo().search([('is_job_location', '=', True)])
        for i in location_ids:
            job_ids = request.env['hr.job'].sudo().search(
                [('website_publish', '=', True), ('address_id', '=', i.id), ('state', '=', 'recruit')])
            job_lst = []
            for j in job_ids:
                job_lst.append({
                    'id': j.id,
                    'title': j.name or ' ',
                    'description': j.description or ' ',
                    'company_name': j.company_id.name,
                    'company_id': j.company_id.id,
                    'address_id': j.address_id.id,
                    'job_type': dict(j._fields['job_type'].selection).get(j.job_type),
                    'no_of_recruitment': j.no_of_recruitment,
                    'image_url': '/web/image?model=hr.job&id=%s&field=image_av' % (j.id) \
                        if j.image_av else '/ppts_website_theme/static/src/img/op1.jpg',
                    'department_id': j.department_id.career_type,
                })

            location_lst.append({
                'id': i.id,
                'jobs_tab': job_lst,
            })

        values = {
            'all_jobs': all,
            'locations_ids': location_lst,
        }
        return request.render('ppts_website_theme.theme_career_page', values)

    # @http.route(['/welliness/retreats/<int:retreat_id>'], type='http', auth="public", website=True)
    # def welliness_retreats_theme_sub(self, retreat_id, **post):
    #   retreat = request.env['calendar.appointment.type'].sudo().browse(retreat_id)
    #   values = {
    #       'retreat_id': retreat,
    #   }
    #   return request.render('ppts_website_theme.website_wellness_retreats_single_page', values)

    @http.route(['/recruitement/application/submit/<int:job_id>'], type='http', methods=['POST'], auth="public", website=True, csrf=False)
    def recruitement_application_submit(self, job_id, **kw):
        job = request.env['hr.job'].sudo().browse(job_id)
        ap_id = request.env['hr.applicant'].sudo().create({
            'job_id': job_id,
            'name': 'Illumination ' + job.name + ' Job Application',
            'partner_name': kw['name'],
            'partner_mobile': kw['contact'],
            'email_from': kw['email'],
            'designation': kw['designation'],
            'work_experience': kw['work_exp'],
            'notice_period': kw['notice_period'],
            'company_id': int(kw['location'] or 1),
        })

        request.env['ir.attachment'].sudo().create({
            'name': kw.get('resume').filename,
            'type': 'binary',
            'datas': base64.b64encode(kw.get('resume').read()),
            'res_model': 'hr.applicant',
            'res_id': ap_id.id
        })

        msg = 'Thanks for submiting the application we will send updates to '+ kw['email']
        return http.request.render("ppts_website_theme.theme_success_page", {"title": 'Your Application Submited SUCCESSFULLY!',"msg":msg})

    @http.route(['/general_enquiry'], type='http', auth="public", website=True, csrf=False)
    def general_enquiry(self, **kwargs):
        master_aboutus_id = request.env['master.aboutus'].search([('name','=','Social Media')])
        partner_id = request.env['res.partner'].search([('email','=',kwargs.get('email', '')),('mobile','=',kwargs.get('phone', ''))],limit=1)
        context = {}
        if kwargs:
            context['name'] = kwargs.get('full_name', '') 
            context['phone'] = kwargs.get('phone', '') 
            context['subject'] = kwargs.get('subject', '')
            context['email'] = kwargs.get('email', '') 


        crm_data = {
        'partner_id':partner_id.id or False,
        'contact_name': kwargs.get('full_name', ''),
        'email_from':partner_id.email or kwargs.get('email', '') ,
        'mobile':partner_id.mobile or kwargs.get('phone', '') ,
        'name':kwargs.get('subject',''),
        'master_aboutus':master_aboutus_id.id,
        }
        crm_id = request.env['crm.lead'].sudo().create(crm_data)
        msg = '<div class="alert alert-success"><strong>Success ! </strong>Thanks for the Enquiry.</div>'
        template_id = request.env.ref('ppts_website_theme.enquiry_mail_template')
        send = template_id.with_context(context).sudo().send_mail(crm_id.id, force_send=True)
     
        return http.request.render("ppts_website_theme.theme_success_page", {"msg":msg})

    @http.route(['/faq_enquiry'], type='http', auth="public", website=True, csrf=False)
    def faq_enquiry(self, **kwargs):
        master_aboutus_id = request.env['master.aboutus'].search([('name','=','Social Media')])
        partner_id = request.env['res.partner'].search([('mobile','=',kwargs.get('phone', ''))],limit=1)
        context = {}
        if kwargs:
            context['name'] = kwargs.get('name', '') 
            context['phone'] = kwargs.get('phone', '') 
            context['subject'] = kwargs.get('subject', '') 
            
        crm_data = {
        'partner_id':partner_id.id or False,
        'contact_name': kwargs.get('name', ''),
        'mobile':partner_id.mobile or kwargs.get('phone', '') ,
        'name':kwargs.get('subject',''),
        'master_aboutus':master_aboutus_id.id,
        }
        crm_id = request.env['crm.lead'].sudo().create(crm_data)
        msg = '<div class="alert alert-success"><strong>Success ! </strong>Thanks for the Enquiry.</div>'
        template_id = request.env.ref('ppts_website_theme.faq_mail_template')
        send = template_id.with_context(context).sudo().send_mail(crm_id.id, force_send=True)
     
        return http.request.render("ppts_website_theme.theme_success_page", {"msg":msg}) 


    @http.route(['/contactus/feedback/location'], type='http', auth="public", website=True, csrf=False, cors='*')
    def contactus_location(self, **post):
        Dropdown = ''
        company_id = request.env['res.company'].sudo().search([])
        Dropdown += '<option value="" disabled selected>Location</option>'
        for i in company_id:
            Dropdown += '<option value="'+ str(i.id) +'" data-oe-model="'+ str(i.id) +'">'+ i.name +'</option>'
        return Dropdown

    @http.route(['/contactus/feedback/category'], type='http', auth="public", website=True, csrf=False, cors='*')
    def contactus_feedback_category(self, **post):
        Dropdown = ''
        feedback_category_id = request.env['feedback.category'].sudo().search([('website_publish','=',True)])
        Dropdown += '<option value="" disabled selected>Feedback Category</option>'
        for each in feedback_category_id:
            Dropdown += '<option value="'+ str(each.id) +'" data-oe-model="'+ str(each.id) +'">'+ each.name +'</option>'
        return Dropdown

    @http.route(['/home/featuredin/image'], type='http', auth="public", website=True, csrf=False, cors='*')
    def get_featured_image(self, **post):
        featured_id = request.env['featured.in'].sudo().search([('website_publish','=',True)])
        image =[]
        for each in featured_id:
            image.append({
                    'image':'/web/image?model=featured.in&id=%s&field=featured_image' % (each.id),
                    'id':each.id,
                    'name':each.name
            })
        return json.dumps(image)

    @http.route(['/get/company/address'], type='http', auth="public", website=True, csrf=False, cors='*')
    def get_company_address(self, **post):
        if post and 'company_id' in post:
            comapny_id = request.env['res.company'].sudo().browse(int(post['company_id']))
            return comapny_id.get_company_address()

    @http.route(['/blog/latest'], type='http', auth="public", website=True)
    def theme_blog_latest(self, **post):
        return request.render('ppts_website_theme.blog_post_short_latest_this_month')

    @http.route(['/blog/global/search'], type='http', auth="public", website=True, csrf=False)
    def theme_blog_global_search(self, **post):
        blog = []
        blog_ids = request.env['blog.post'].sudo().search(['|', ('name', 'ilike', str(post['search'])), ('subtitle', 'ilike', str(post['search']))])

        for i in blog_ids:
            blog.append({
                'name': i.name,
                'id': i.id,
                'url': '/blog/'+ slug(i.blog_id) +'/'+ str(i.id),
                'slug': slug(i.blog_id),
            })
        return json.dumps(blog)

    @http.route(['/blog/latest/tag/filter'], type='http', auth="public", website=True, csrf=False, cors="*")
    def blog_latest_tag_filter(self, **post):
        tag_ids = json.loads(post['filter'])
        tag_ids = [int(i) for i in tag_ids];blog = []
        domain = [('is_published','=',True)]
        if tag_ids:
            domain.append(('tag_ids','in',tag_ids))
        blog_ids = request.env['blog.post'].sudo().search(domain, order='visits desc')
        for i in blog_ids:
            tags = []
            for f in i.tag_ids: tags.append(f.name)
            blog.append({
                'name': i.name,
                'subtitle': i.subtitle or '',
                'id': i.id,
                'url': '/blog/'+ slug(i.blog_id) +'/'+ str(i.id),
                'slug': slug(i.blog_id),
                'tags': tags,
                'img': '/web/image?model=blog.post&amp;id='+str(i.id)+'&amp;field=image_av' if i.image_av else '/ppts_website_theme/static/src/img/rc1.jpg',
            })
        return json.dumps(blog)


    @http.route(['/blog/global/search/list/cards'], type='http', auth="public", website=True, csrf=False)
    def blog_global_search_list_cards(self, **post):
        blog = []
        blog_ids = request.env['blog.post'].sudo().search(['|',('name','ilike', str(post['search'])),('subtitle','ilike',str(post['search']))],limit=3)
        for i in blog_ids:
            tags = []
            for f in i.tag_ids: tags.append(f.name)

            blog.append({
                'name': i.name,
                'subtitle': i.subtitle or '',
                'id': i.id,
                'url': '/blog/'+ slug(i.blog_id) +'/'+ str(i.id),
                'slug': slug(i.blog_id),
                'tags': tags,
                'img': '/web/image?model=blog.post&amp;id='+str(i.id)+'&amp;field=image_av' if i.image_av else '/ppts_website_theme/static/src/img/rc1.jpg',
            })
        return json.dumps(blog)

    @http.route(['/home/our/excepts'], type='http', auth="public", website=True, csrf=False, cors='*')
    def get_excepts_image(self, **post):
        employee_id = request.env['hr.employee'].sudo().search([('feature_in_homepage','=',True)])
        employee =[]
        for each in employee_id:
            job =""
            for each_name in each.by_support:
                job = each_name.name + "/" + job
            employee.append({
                    'image':'/web/image?model=hr.employee&id=%s&field=image_1920' % (each.id),
                    'id':each.id,
                    'name':each.name,
                    'job':job[:-1]

            })
        return json.dumps(employee)


    @http.route(['/home/client/about'], type='http', auth="public", website=True, csrf=False, cors='*')
    def get_client_about(self, **post):
        testimonial_ids = request.env['testimonial'].sudo().search([('website_publish','=',True),('feature_in_homepage','=',True)])
        testimonial =[]
        for each in testimonial_ids:
            testimonial.append({
                    'image':'/web/image?model=testimonial&id=%s&field=image_av' % (each.id),
                    'id':each.id,
                    'name':each.description,
                    'employee_id':each.employee_id.name,
            })
        return json.dumps(testimonial)

    @http.route(['/wellness/page/filter'], type='http', auth="public", website=True, csrf=False)
    def wellness_page_filter(self, **post):
        domain =[]
        retreat_id = request.env['appointment.category'].sudo().search([('is_retreats','=',True)], limit=1)
        domain = [('event_service_categ_id','=',retreat_id.id),('stage_id','in',('Published','Announced'))]
        wellness = []
        event_date = ""
        if 'location-filter' in post and post['location-filter'] != '':
            domain.append(['company_id','=',int(post['location-filter'])])
        event_ids = request.env['event.event'].sudo().search(domain, limit=4)
        for i in event_ids:
            if 'number-day-filter' in post and post['number-day-filter'] != '':
                if len(i.multi_date_line_ids.ids) ==  int(post['number-day-filter']):
                    if i.event_multiple_date == 'oneday':
                        event_date = i.s_start_date.strftime("%d %B")
                    if i.event_multiple_date == 'multiday':
                        start = request.env['multi.date.line'].sudo().browse(i.multi_date_line_ids.ids[0])
                        end = request.env['multi.date.line'].sudo().browse(i.multi_date_line_ids.ids[-1])
                        event_date = start.date_begin.strftime("%d %B")+ ' To ' + end.date_begin.strftime("%d %B")
                    wellness.append({
                        'image': '/web/image?model=event.event&amp;id=%s&amp;field=image' % (i.id) if  i.image else '/ppts_website_theme/static/src/img/uc1.jpg',
                        'id': i.id,
                        'name':i.name,
                        'location_id': i.company_id.name,
                        'date': event_date,
                        'event_sub_categ_id': i.event_sub_categ_id.name,
                        'facilitator': i.get_facilitator_name(),
                        'platform': dict(i._fields['type_event'].selection).get(i.type_event),
                        'price': i.get_event_price(),
                    }) 
            else:
                if i.event_multiple_date == 'oneday':
                    event_date = i.s_start_date.strftime("%d %B")
                if i.event_multiple_date == 'multiday':
                    start = request.env['multi.date.line'].sudo().browse(i.multi_date_line_ids.ids[0])
                    end = request.env['multi.date.line'].sudo().browse(i.multi_date_line_ids.ids[-1])
                    event_date = start.date_begin.strftime("%d %B")+ ' To ' + end.date_begin.strftime("%d %B")
                wellness.append({
                    'image': '/web/image?model=event.event&amp;id=%s&amp;field=image' % (i.id) if  i.image else '/ppts_website_theme/static/src/img/uc1.jpg',
                    'id': i.id,
                    'name':i.name,
                    'location_id': i.company_id.name,
                    'date': event_date,
                    'event_sub_categ_id': i.event_sub_categ_id.name,
                    'facilitator': i.get_facilitator_name(),
                    'platform': dict(i._fields['type_event'].selection).get(i.type_event),
                    'price': i.get_event_price(),
                })
        return json.dumps(wellness)
            
                
            # elif 'number-day-filter' in post and post['number-day-filter'] == '':
            #   # add_json()
            #   wellness.append({
            #           'image': '/web/image?model=event.event&amp;id=%s&amp;field=image' % (i.id) if  i.image else '/ppts_website_theme/static/src/img/uc1.jpg',
            #           'id': i.id,
            #           'name':i.name,
            #           'location_id': i.address_id.name,
            #           'date': i.s_start_date.strftime("%d.%m.%Y") or '',
            #           'event_sub_categ_id': i.event_sub_categ_id.name,
            #           'facilitator': i.get_facilitator_name(),
            #           'platform': dict(i._fields['type_event'].selection).get(i.type_event),
            #           'price': i.get_event_price(),
            #       })
            #   return json.dumps(wellness)

    @http.route(['/career/ask/anything/submit'], type='http', method="['POST']", auth="public", website=True, csrf=False)
    def career_submit(self, **post):
        stage = request.env['helpdesk.stage'].sudo().search([('sequence', '=', 0)])
        context = {}
        if post:
            context['name'] = post.get('full_name', '')
            context['phone'] = post.get('phone', '')
            context['subject'] = post.get('subject', '')
            context['email'] = post.get('email', '')

        helpdesk_data = {
            'partner_name': post.get('full_name', ''),
            'stage_id': stage.id,
            'name': "Ask Us Any Thing",
            'description': post.get('subject', ''),
            'partner_email': post.get('email', ''),
            'partner_mobile': post.get('phone', ''),

        }
        helpdesk_id = request.env['helpdesk.ticket'].sudo().create(helpdesk_data)
        template_id = request.env.ref('ppts_website_theme.ask_for_anything_mail_template')
        send = template_id.with_context(context).sudo().send_mail(helpdesk_id.id, force_send=True)
        if 'email' in post:
            msg = 'Thanks for submitting your request. We will send updates to ' + post.get('email', '')
        else:
            msg = 'Thanks for submitting your request. We will send updates to ' + post.get('phone', '')
        user = request.env.user
        return http.request.render("ppts_website_theme.theme_success_page",
                                   {"title": 'Your Request Submited SUCCESSFULLY!', "msg": msg, 'user_id': user})

    @http.route(['/newsletter/submit'], type='http', method="['POST']", auth="public", website=True, csrf=False)
    def newsletter_submit(self, **post):
        request.env['mailing.contact'].create({
            'email': post['email'],
            'subscription_list_ids': [(6, 0, request.env['mailing.list'].sudo().search([('is_newsletter','=',True)]).ids)]
        })

    @http.route(['/homepage/feature/blog'], type='http', auth="public", website=True, csrf=False)
    def homepage_feature_blog(self, **kwargs):
        blog_ids = request.env['blog.post'].sudo().search([('is_published','=',True),('feature_post','=',True)], limit=5)
        blog_vals = []
        for each_blog in blog_ids:
            blog_tag =[]
            for each_tag in each_blog.tag_ids[:2]:
                blog_tag.append(each_tag.name)
            blog_vals.append({
                'image': '/web/image?model=blog.post&id=%s&field=image_av' % (each_blog.id) if each_blog.image_av else '/ppts_website_theme/static/src/img/rc1.jpg',
                'id':each_blog.id,
                'name':each_blog.name,
                'blog_tag_ids':blog_tag,
                'subtitle':each_blog.subtitle,
                'author_id':each_blog.author_id.name,
                'visits':each_blog.visits,
                'date':each_blog.create_date.strftime("%d.%m.%Y"),
                'url': '/blog/%s/%s' % (slug(each_blog.blog_id), each_blog.id),
            })
        return json.dumps(blog_vals)

    @http.route(['/livechat/get/session/channel'], type='http', auth="public", website=True, csrf=False)
    def livechat_get_session_channel(self, **post):
        print('get session id', post)
        username = post['fname']
        channel = request.env['im_livechat.channel'].sudo().search([],limit=1)
        info = channel.get_livechat_info(username=username)

        print(request.website.channel_id,'------- request.website.channel_id')
        if request.website.channel_id:
            # livechat_info = request.website.channel_id.sudo().get_livechat_info()
            if info['available']:
                print(11111111111111111)
                livechat_request_session = request.website._get_livechat_request_session()
                if livechat_request_session:
                    print(2222222222222222222222222)
                    livechat_request_session['folded'] = False
                    info['options']['chat_request_session'] = livechat_request_session
            # return livechat_info

        print(info,'-------==-======')

        liveSession = {
            'available': info.get('available'),
            'server_url': info.get('server_url'),
            'options': info.get('options'),
        }

        return json.dumps(liveSession)
        # return request.render('im_livechat.loader', {'info': info, 'web_session_required': True}, headers=[('Content-Type', 'application/javascript')])
    
    
        


class WebsiteSale(WebsiteSale):

    @http.route(['/attachment/download',], type='http', auth='public')
    def download_attachment(self, attachment_id):
        # Check if this is a valid attachment id
        attachment = request.env['ir.attachment'].sudo().search([('id', '=', int(attachment_id))])

        if attachment:
            attachment = attachment[0]
        else:
            return request.redirect('/press_media')

        if attachment["type"] == "url":
            if attachment["url"]:
                return request.redirect(attachment["url"])
            else:
                return request.not_found()
        elif attachment["datas"]:
            data = io.BytesIO(base64.standard_b64decode(attachment["datas"]))
            return http.send_file(data, filename=attachment['name'], as_attachment=True)
        else:
            return request.not_found()

    @http.route(['/shop/checkout'], type='http', auth="public", website=True, sitemap=False)
    def checkout(self, **post):
        res = super(WebsiteSale, self).checkout()
        if post.get('event'):
            res.qcontext["is_event"] = True
        return res

    @http.route(['/shop/payment'], type='http', auth="public", website=True, sitemap=False)
    def payment(self, **post):
        res = super(WebsiteSale, self).payment()
        if post.get('event'):
            res.qcontext["is_event"] = True
            res.qcontext["event_id"] = request.env['event.event'].sudo().browse(int(post.get('event')))
        else:
            res.qcontext["is_event"] = False
        return res

    @http.route(['/shop/pricelist'], type='http', auth="public", website=True, sitemap=False)
    def pricelist(self, promo, **post):
        res = super(WebsiteSale, self).pricelist(promo)
        redirect = post.get('r', '/shop/cart')
        redirect = post.get('r', '/shop/payment')
        # empty promo code is used to reset/remove pricelist (see `sale_get_order()`)
        if promo:
            pricelist = request.env['product.pricelist'].sudo().search([('code', '=', promo)], limit=1)
            if (not pricelist or (pricelist and not request.website.is_pricelist_available(pricelist.id))):
                if '?event' in post and 'r' in post:
                    return request.redirect("%s&code_not_available=1" % redirect)
                else:
                    return request.redirect("%s?code_not_available=1" % redirect)
        else:
            return request.redirect("%s?code_not_available=1" % redirect)
        return res


class WebsiteEventControllerCustom(WebsiteEventController):

    @http.route(['''/event/<model("event.event"):event>/register'''], type='http', auth="public", website=True, sitemap=False)
    def event_register(self, event, **post):
        if not event.can_access_from_current_website():
            raise werkzeug.exceptions.NotFound()

        retreat_id = request.env['appointment.category'].sudo().search([('is_retreats','=',True)], limit=1)
        values = self._prepare_event_register_values(event, **post)
        values['ticket'] = event.event_ticket_ids[0] if len(event.event_ticket_ids) > 0 else 0

        if event.event_service_categ_id.id == retreat_id.id:
            return request.render("ppts_website_theme.website_wellness_retreats_single_page", values)
        else:
            return request.render("website_event.event_description_full", values)

    @http.route(['''/event/<model("event.event"):event>/registration/customer/details'''], type='http', auth="public", methods=['POST'], website=True)
    def customer_details_event_book(self, event, **post):
        if not event.can_access_from_current_website():
            raise werkzeug.exceptions.NotFound()

        tickets = self._process_tickets_form(event, post)
        availability_check = True
        if event.seats_limited:
            ordered_seats = 0
            for ticket in tickets:
                ordered_seats += ticket['quantity']
            if event.seats_available < ordered_seats:
                availability_check = False
        if not tickets:
            return False
        return request.render("ppts_website_theme.checkout_book_an_event",  {'tickets': tickets, 'event': event, 'availability_check': availability_check})

    def _process_attendees_form(self, event, form_details):
        """ Process data posted from the attendee details form.

        :param form_details: posted data from frontend registration form, like
            {'1-name': 'r', '1-email': 'r@r.com', '1-phone': '', '1-event_ticket_id': '1'}
        """
        allowed_fields = {'name', 'phone', 'email', 'mobile', 'event_id', 'partner_id', 'event_ticket_id', 'country_id', 'city_id'}
        registration_fields = {key: v for key, v in request.env['event.registration']._fields.items() if
                               key in allowed_fields}
        registrations = {}
        global_values = {}
        for key, value in form_details.items():
            counter, attr_name = key.split('-', 1)
            field_name = attr_name.split('-')[0]
            if field_name not in registration_fields:
                continue
            elif isinstance(registration_fields[field_name], (fields.Many2one, fields.Integer)):
                value = int(value) or False  # 0 is considered as a void many2one aka False
            else:
                value = value

            if counter == '0':
                global_values[attr_name] = value
            else:
                registrations.setdefault(counter, dict())[attr_name] = value
        for key, value in global_values.items():
            for registration in registrations.values():
                registration[key] = value

        return list(registrations.values())

    @http.route(['''/event/<model("event.event"):event>/registration/checkout'''], type='http', auth="public", methods=['POST'], website=True)
    def registration_checkout(self, event, **post):
        if not event.can_access_from_current_website():
            raise werkzeug.exceptions.NotFound()

        registrations = self._process_attendees_form(event, post)
        attendees_sudo = self._create_attendees_from_registration_post(event, registrations)
        # we have at least one registration linked to a ticket -> sale mode activate
        if any(info['event_ticket_id'] for info in registrations):
            order = request.website.sale_get_order(force_create=False)
            if order.amount_total:
                return request.redirect("/shop/payment?event="+ str(event.id))
            # free tickets -> order with amount = 0: auto-confirm, no checkout
            elif order:
                order.action_confirm()  # tde notsure: email sending ?
                request.website.sale_reset()

        return request.render("website_event.registration_complete",  self._get_registration_confirm_values(event, attendees_sudo))


    @http.route(['/wellness/retreat/speaker'], type='http', auth="public", website=True, csrf=False, cors='*')
    def get_speaker_image(self, **post):
        employee_id = request.env['hr.employee'].sudo().search([('feature_in_wellness','=',True)])
        employee =[]
        for each in employee_id:
            job =""
            for each_name in each.by_support:
                job = each_name.name + "/" + job
            employee.append({
                    'image':'/web/image?model=hr.employee&id=%s&field=image_1920' % (each.id),
                    'id':each.id,
                    'name':each.name,
                    'job':job[:-1]

            })
        return json.dumps(employee)

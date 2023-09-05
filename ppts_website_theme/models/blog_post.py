# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime

class BlogPost(models.Model):
    _inherit = 'blog.post'
    _description = 'Blog Post'


    def _compute_author_count(self):
        blog_data = self.read_group([], ['author_id'], ['author_id'])
        result = dict((data['author_id'][0], data['author_id_count']) for data in blog_data)
        sort_result = sorted(result.items(), key=lambda x: (-x[1], x[0]))[0:5]
        vals = list((sort_data[0]) for sort_data in sort_result)
        return vals


    def get_post_date(self): return self.post_date.strftime("%d.%m.%Y")
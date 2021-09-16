# -*- coding: utf-8 -*-
from sitetree.utils import tree, item


sitetrees = (
    tree('main', title='Main Menu', items=[
        item('Home', 'home', in_menu=True, in_sitetree=True, url_as_pattern=True, children=[
            item('About', 'about', in_menu=True, in_sitetree=True, url_as_pattern=True),
            item('Contact', 'contact', in_menu=True, in_sitetree=True, url_as_pattern=True),
        ]),
#       item('Test', 'test', in_menu=True, in_sitetree=True, url_as_pattern=True, access_loggedin=True),
#       item('Articles', 'articles', in_menu=True, in_sitetree=True, url_as_pattern=True),
#       item('News', 'news', in_menu=True, in_sitetree=True, url_as_pattern=True),
        # item('Articles', 'articles-listing', children=[
        #     item('{{ article.title }}', 'articles-details', in_menu=False, in_sitetree=False),
        #     item('Add article', 'article-add', access_by_perms=['main.allow_article_add']),
        #     item('Edit: {{ article.title }}', 'articles-edit', in_menu=False, in_sitetree=False)
        # ])
    ]),
)

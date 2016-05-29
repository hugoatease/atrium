from functools import wraps
from flask_restful import marshal
from flask import request


class pagination_helper(object):
    def __init__(self, fields, envelope=None):
        self.fields = fields
        self.envelope = envelope

    def __call__(self, func):
        @wraps(func)
        def paginated(*args, **kwargs):
            query = func(*args, **kwargs)
            page = int(request.args['page']) if 'page' in request.args else 1
            limit = int(request.args['limit']) if 'limit' in request.args else 20
            paginated = query.paginate(page, per_page=limit)

            result = {
                'results': marshal(paginated.items, self.fields, self.envelope),
                'pages': paginated.pages
            }

            if paginated.has_next:
                result['next_page'] = paginated.next_num
            if paginated.has_prev:
                result['previous_page'] = paginated.prev_num

            return result

        return paginated

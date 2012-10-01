import math

from eplasty.query import SelectQuery
from eplasty.ctx import get_session

class Pager(object):
    """Pager wraps around some other class and allows to create pages from some
    data-set. It can be created directly but it is recommended to use 
    ObjectClass.paginate().
    Arguments:

    class_ - The object class to page from.
    page_size - The size of a single page.
    base - The number of the first page. Defaults to 1.
    widow_size - If the last page size would be ``widow_size`` or smaller
        the previous page becomes the last and is bigger than ``page_size``.
        Defaults to 0 (which means no widow control).
    the rest of kwargs will be passed to query
    """

    def __init__(self, class_, page_size, base=1, widow_size=0, **kwargs):
        self.class_ = class_
        self.page_size = page_size
        self.base = base
        self.widow_size = widow_size
        self.kwargs = kwargs

    def get_page(self, page_no, session=None):
        """Returns the data for the page of a given_number."""
        kwargs = self.kwargs.copy()
        real_page_no = page_no - self.base
        page_size = self.page_size
        full_size = self.get_full_count()
        kwargs['offset'] = offset = real_page_no * page_size
        if offset + self.widow_size >= full_size:
            return []
        if offset + page_size + self.widow_size >= full_size:
            kwargs['limit'] = None
        else:
            kwargs['limit'] = page_size
        print('FULL: {0}, PAGE: {1}, OFFSET: {2}, LIMIT: {3}'.format(full_size, real_page_no, offset, kwargs['limit']))
        return self.class_.find(session=session, **kwargs)

    def get_page_count(self, session=None):
        """Returns the number of pages. Note that for base = 1 i would be a
        number of the last page, while for base = 1, the last page number is 
        get_page_count() - 1"""
        return math.ceil(
            (self.get_full_count(session) - self.widow_size) / self.page_size
        )


    def get_full_count(self, session=None):
        """Returns the full size of the dataset."""
        q = SelectQuery(from_=self.class_.__table_name__, columns=('COUNT(*)',))
        session = get_session(session)
        cursor = session.cursor()
        cursor.execute(*q.render())
        return cursor.fetchall()[0][0]

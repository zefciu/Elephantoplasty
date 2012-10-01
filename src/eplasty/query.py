"""Objects that facilitate building various SQL Queries"""
import eplasty as ep

class SelectQuery(object):
    """Object that represents an SQL SELECT query and facilitates its creation
        Parameters:
        * from_ - the name of the table to select from
        * conditions - an eplasty.Condition instance
        * columns - an iterable of columns or column names to load 
          (SELECT CLAUSE)
        * joins - joins as a list of joins as tuples
          in format (join type, table name, ON condtion)
        * limit - an integer or None for no limit
        * offset - an integer or None for no offset
    """

    def __init__(
        self, from_, condition=ep.conditions.All(), columns='*', joins=False,
        order=None, limit=None, offset=None
    ):
        self.from_ = from_
        self.condition = condition
        self.columns = columns
        self.joins = joins or []
        self.order = order or []
        self.limit = limit
        self.offset = offset

    def _render_columns(self):
        """Renders the SELECT clause"""
        if self.columns == '*':
            return '*'
        else:
            return ', '.join((
                self._get_column_name(column) for column in self.columns
            ))

    def _get_column_name(self, column):
        """Renders a single column name (works on a column or a string)"""
        if isinstance (column, ep.column.Column):
            return column.render_full()
        else:
            return column

    def _render_from(self):
        """Renders the FROM clause"""
        buff = [self.from_]
        variables = []
        for j in self.joins:
            type_, table, l_column, r_column = j
            type_ = type_ or ''
            buff.append(' {type_} JOIN {table} ON {l_column} = {r_column}'.\
                format(
                    type_ = type_,
                    table = table,
                    l_column = l_column,
                    r_column = r_column,
                )
            )
            variables
        return ''.join(buff), variables

    def _render_order(self):
        """Renders the ORDER BY clause"""
        if self.order:
            parts = []
            for column, direction in self.order:
                parts.append('{0} {1}'.format(
                    self._get_column_name(column), direction)
                )
            return ' ORDER BY ' + ', '.join(parts)
        else:
            return ''

    def _render_limit_offset(self):
        """Renders the limit and offset clauses as a tuple.
        Can return an empty string + empty tuple."""
        result_string = []
        result_vars = []
        if self.limit:
            result_string.append('LIMIT %s')
            result_vars.append(self.limit)
        if self.offset:
            result_string.append('OFFSET %s')
            result_vars.append(self.offset)
        if result_string:
            return (' ' + ' '.join(result_string), tuple(result_vars))
        else:
            return ('', tuple())

    def render(self):
        """Renders the query"""
        select_clause = self._render_columns()
        from_clause, from_vars = self._render_from()
        where_clause, where_vars = self.condition.render()
        order_clause = self._render_order()
        limit_offset_clause, limit_offset_vars = self._render_limit_offset()
        return (
            (
                'SELECT {select_clause} FROM {from_clause}'
                ' WHERE {where_clause}{order_clause}{limit_offset_clause};'
            ).format(**locals()),
            where_vars + limit_offset_vars
        )

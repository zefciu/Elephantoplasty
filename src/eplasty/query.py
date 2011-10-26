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
    """

    __slots__ = ['from_', 'condition', 'columns', 'joins', 'order']

    def __init__(
        self, from_, condition=ep.conditions.All(), columns='*', joins=False,
        order = None
    ):
        self.from_ = from_
        self.condition = condition
        self.columns = columns
        self.joins = joins or []
        self.order = order or []

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

    def render(self):
        """Renders the query"""
        select_clause = self._render_columns()
        from_clause, from_vars = self._render_from()
        where_clause, where_vars = self.condition.render()
        order_clause = self._render_order()
        return (
            (
                'SELECT {select_clause} FROM {from_clause}'
                ' WHERE {where_clause}{order_clause};'
            ).format(**locals()),
            where_vars
        )

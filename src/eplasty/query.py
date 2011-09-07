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

    __slots__ = ['from_', 'condition', 'columns', 'joins']

    def __init__(
        self, from_, condition=ep.conditions.All(), columns='*', joins=[]
    ):
        self.from_ = from_
        self.condition = condition
        self.columns = columns
        self.joins = joins

    def _render_columns(self):
        """Renders the SELECT clause"""
        if self.columns == '*':
            return '*'
        else:
            return ','.join((self._get_column_name(c) for c in self.columns))

    def _get_column_name(self, c):
        """Renders a single column name (works on a column or a string)"""
        if isinstance (c, ep.column.Column):
            return '.'.join([c.owner_class.__table_name__, c.name])
        else:
            return c

    def _render_from(self):
        """Renders the FROM clause"""
        buff = [self.from_]
        variables = []
        for j in self.joins:
            type_, table, condition = j
            type_ = type_ or ''
            cond_txt, cond_variables = condition.render()
            buff.append('{type_} JOIN {table} ON {condition}'.format(
                type_ = type_,
                table = table,
                condition = cond_txt
            ))
            variables += cond_variables
        return ''.join(buff), variables

    def render(self):
        """Renders the query"""
        select_clause = self._render_columns()
        from_clause, from_vars = self._render_from()
        where_clause, where_vars = self.condition.render()
        return (
            (
                'SELECT {select_clause} FROM {from_clause}'
                ' WHERE {where_clause}'
            ).format(**locals()),
            where_vars
        )

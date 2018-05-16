from marshmallow import fields


class JoinNested(fields.Nested):

    def __init__(self, **kwargs):

        self.table = kwargs.pop('table')
        self.joinOn = kwargs.pop('joinOn')
        self.joinType = kwargs.pop('joinType', 'JOIN')

        if self.joinOn is None and self.table is None:
            raise Exception(
                'Please set foreign index name and table name'
                'for join statement'
            )
        super(JoinNested, self).__init__(**kwargs)

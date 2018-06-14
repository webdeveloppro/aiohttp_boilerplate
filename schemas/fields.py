import json

from marshmallow import fields, validate


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


class Choice(fields.Raw):
    type = 'choice'

    def get_validation(self):
        return {
            "required": self.required,
            "oneOf": self.choices,
        }

    def __init__(self, **kwargs):
        choices = kwargs.pop('choices')
        v = kwargs.pop('validate', [])

        if type(choices) == list:
            v.append(validate.OneOf(
                [x['value'] if 'value' in x else x for x in choices],
                [x['name'] if 'name' in x else x for x in choices],
            ))
        else:
            v.append(validate.OneOf(
                [x for x in choices],
                [choices[x] for x in choices],
            ))
        kwargs['validate'] = v
        super(Choice, self).__init__(**kwargs)


class ChoiceConst(Choice):
    ''' Create choice field from json const array '''
    type = 'choice'

    def get_validation(self):
        return {
            "required": self.required,
            "oneOf": self.const_file,
        }

    def __init__(self, const_file, const_folder='const', **kwargs):

        file_name, const_name = const_file.rsplit('.', 1)
        file_name = file_name.replace('.', '/')
        file_path = const_folder + '/' + file_name + '.json'
        data = json.loads(open(file_path).read())
        kwargs['choices'] = data[const_name]
        self.const_file = const_file
        super(Choice, self).__init__(**kwargs)

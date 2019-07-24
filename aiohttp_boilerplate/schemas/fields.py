import json

from marshmallow import fields, validate, Schema


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
        super().__init__(**kwargs)


class Choice(fields.Raw):
    type = 'choice'

    def get_validation(self):
        return {
            "required": self.required,
            "oneOf": self.choices,
        }

    def __init__(self, choices, **kwargs):
        self.choices = choices
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
        super().__init__(**kwargs)


class ChoiceConst(Choice):
    ''' Create choice field from json const array '''
    type = 'choice'

    def get_validation(self):
        return {
            "required": self.required,
            "oneOf": self.const_file,
        }

    def __init__(self, const_file, const_folder='const', **kwargs):
        if '.' in const_file:
            file_name, const_name = const_file.rsplit('.', 1)
        else:
            file_name, const_name = const_file, None
        file_name = file_name.replace('.', '/')
        file_path = const_folder + '/' + file_name + '.json'
        data = json.loads(open(file_path).read())
        choices = data.get(const_name, data)
        self.const_file = const_file
        super().__init__(choices, **kwargs)


class FileRow(Schema):
    id = fields.Integer()
    url = fields.String()
    name = fields.Str()
    mime = fields.Str()
    bucket_id = fields.Int()
    meta_data = fields.Dict()


class FolderRow(Schema):
    files = fields.Nested(FileRow, required=True, many=True)
    meta_data = fields.Dict()

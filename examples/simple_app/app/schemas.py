from marshmallow import Schema, fields


class PostSchema(Schema):
    id = fields.Int()
    name = fields.Str()
    content = fields.Str()

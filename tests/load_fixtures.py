import datetime
import json


class LoadFixture:

    def __init__(self, file_name, directory="./", table=None):
        self.table = table
        self.directory = directory

        if len(file_name) == 0:
            raise Exception("You have to set up a json file")

        self.data = []
        self.file = file_name

        if self.table is None:
            self.get_table()

    def remove_ext(self, t=None):

        if t is None:
            t = self.file

        try:
            return t.rsplit('.', 1)[0]
        except ValueError:
            return t

    def get_table(self):
        '''
            Tranfrom 01_<table_name>.json to table_name
            remove everything after first .
            remove before first _
        '''

        if self.table is None:
            t = self.file
            try:
                t = self.remove_ext(t)
                idx = t.index("_")
                int(t[0:idx])
                t = t[idx + 1:]
            except ValueError:
                pass

            self.table = t

    async def file2db(self, con):
        ''' Read data from file and save in the data array '''
        filename = self.directory + '/' + self.file

        self.data = json.loads(open(filename, 'r').read())

        await con.execute("TRUNCATE {} CASCADE".format(self.table))

        for row in self.data:
            field_names = []
            field_placeholders = []

            i = 1
            for f in row.keys():
                field_names.append('"' + f + '"')
                field_placeholders.append('${}'.format(i))
                i += 1
            # FIXME
            sql = "INSERT INTO {} ({}) VALUES ({})".format(  # nosec
                self.table,
                ','.join(field_names),
                ','.join(field_placeholders)
            )
            stmt = await con.prepare(sql)

            # analyze sql fields
            if 'approved_date' in row.keys():
                row['approved_date'] = datetime.datetime.fromtimestamp(row['approved_date'])
                row['closing_date'] = datetime.datetime.fromtimestamp(row['closing_date'])
            if 'publication_date' in row.keys():
                row['publication_date'] = datetime.datetime.fromtimestamp(row['publication_date'])
            if 'last_login' in row.keys():
                row['last_login'] = datetime.datetime.fromisoformat(row['last_login'])
            await stmt.fetch(*row.values())

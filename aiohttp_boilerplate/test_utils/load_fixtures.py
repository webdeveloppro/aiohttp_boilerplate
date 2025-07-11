import datetime
import json
import re


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

    async def truncate(self, con):
        await con.execute(f"TRUNCATE {self.table} CASCADE")

    async def file2db(self, con):
        ''' Read data from file and save in the data array '''
        filename = self.directory + '/' + self.file

        self.data = json.loads(open(filename, 'r').read())

        await con.execute(f"DELETE FROM {self.table}; select setval('{self.table}_id_seq',(select max(id) from {self.table})); ALTER SEQUENCE {self.table}_id_seq RESTART WITH 1;")

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

            # hack to convert strings to dates, expecting dates in iso format "2022-12-29T20:36:42.611271+00:00"
            number_pattern = "\\d{4}-\\d{2}-\\d{2}T\\d{2}.*"
            for key in row.keys():
                val = row[key]
                if isinstance(val, str) and re.match(number_pattern, val) is not None:
                    row[key] = datetime.datetime.fromisoformat(val)
            await stmt.fetch(*row.values())

        # Fix auto increments after
        await con.execute(f"select setval('{self.table}_id_seq', (select max(id)+1 from {self.table}))")

from pythonjsonlogger import jsonlogger


class JsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)
        if log_record.get('level'):
            log_record['level'] = log_record['level'].upper()
            log_record['severity'] = log_record['level'].upper()
        else:
            log_record['level'] = record.levelname
            log_record['severity'] = record.levelname

class Tracker:
    def __init__(self, rule_mapping):
        self.data = Tracker.create_initial_track(rule_mapping)

    @staticmethod
    def create_initial_track(rule_mapping):
        data = {}
        for mapping in rule_mapping:
            rule_id = mapping["rule_id"]
            data[rule_id] = []
            for field in mapping["fields_to_apply"]:
                data[rule_id].append(
                    {
                        "field": field["fields"][0],
                        "applied": False,
                        "valid": None
                    }
                )
        return data

    def update(self, rule_id, field, validity):
        for idx, row in enumerate(self.data[rule_id]):
            if row["field"] == field:
                self.data[rule_id][idx]["valid"] = validity 
                self.data[rule_id][idx]["applied"] = True        

    def read(self, rule_id, field):
        for row in self.data[rule_id]:
            if row["field"] == field:
                return row
from pandas.api.types import is_object_dtype
import pandas as pd
import numpy as np
import re

class Teamgantt:
    _teamgantt_db = None
    def __init__(teamgantt_db, *args, **kwargs):
        self._teamgantt_db = teamgantt_db
    def _entry_is_mapped(entry, *templates):
        results = [lambda entry, template: re.search(template.upper(), entry.upper(), re.IGNORECASE) != None  for template in templates]
        return True in results
    def _map_column_names(self):
        map_arr = {
            "name": ['^name[a-z]*[1-9]*'],
            "type": ['^type[a-z]*[1-9]*'],
            "index": ['^index[a-z]*[1-9]*', "WBS #[a-z]*[1-9]*"],
            "start_date":["^start date[a-z]*[1-9]*"],
            "end_date":["^end date[a-z]*[1-9]*"],
            "notes": ["^notes[a-z]*[1-9]*"]
        }
        _teamgantt_db = self._teamgantt_db.copy()
        for column in _teamgantt_db.columns:
            for key,value in map_arr:
                if(self._entry_is_mapped(column, *value)):
                    _teamgantt_db.rename(columns={column:key}, inplace=True)
                    break
            else:
                _teamgantt_db.drop(column, inplace=True, axis = 1)
        
        self._teamgantt_db = _teamgantt_db
    def _revise_types(self):
        _teamgantt_db = self._teamgantt_db.copy()
        for column in _teamgantt_db.columns:
            if is_object_dtype(_teamgantt_db[column]):
                if column in ["start_date", "end_date"]:
                    _teamgantt_db[column] = pd.to_datetime(_teamgantt_db[column])
                else:
                     _teamgantt_db[column] = _teamgantt_db[column].astype(str)
    def process_database(self):
        self._map_column_names()
        self._revise_types()

from InstituteRetentionAnalyzer.munging.reformat_bobj import *

import pandas as pd

def test_release_status_rename_columns():
	orig_df = pd.DataFrame(columns = ["Person Id", "First Name", "Last Name", "Release Code", "Release Date", "Current Institute", "Release Step"])
	new_df = rename_columns(orig_df)
	assert(set(new_df.columns) == set(['pid','first_name','last_name','release_code','release_date','institute','step']))

def test_institute_transfer_rename_columns():
	orig_df = pd.DataFrame(columns = ['CM History Id', 'Person Id', 'First Name', 'Last Name', 'Institute Name (CM History)', 'CM History Record Update Time'])
	new_df = rename_columns(orig_df)
	assert(set(new_df.columns) ==  set(['history_id','pid','first_name','last_name','institute','history_record_timestamp']))
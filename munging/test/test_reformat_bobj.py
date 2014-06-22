from InstituteRetentionAnalyzer.munging.reformat_bobj import *

import pandas as pd

def test_release_status_rename_bobj_columns():
	orig_df = pd.DataFrame(columns = ["Person Id", "First Name", "Last Name", "Release Code", "Release Date", "Current Institute", "Release Step","Emergency Release Start Date"])
	new_df = rename_bobj_columns(orig_df)
	assert(set(new_df.columns) == set(['pid','first_name','last_name','release_code','release_date','institute','step','er_start_date']))

def test_institute_transfer_rename_bobj_columns():
	orig_df = pd.DataFrame(columns = ['CM History Id', 'Person Id', 'First Name', 'Last Name', 'Institute Name (CM History)', 'CM History Record Update Time'])
	new_df = rename_bobj_columns(orig_df)
	assert(set(new_df.columns) ==  set(['history_id','pid','first_name','last_name','institute','history_record_timestamp']))

def test_fill_exit_date_with_er_date():
	orig_df = pd.DataFrame({'pid':[1],'release_date':[None],'er_start_date':['6/2']})
	new_df = fill_in_release_date(orig_df)
	assert(new_df.release_date.notnull().all())
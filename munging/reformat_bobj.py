import pandas as pd

def rename_bobj_columns(df):		
	column_map = {
		"Person Id"		                : 'pid',
		"First Name"		            : 'first_name',
		"Last Name"		                : 'last_name',
		"Release Code"		            : 'release_code',
		"Release Date"		            : 'release_date',
		"Current Institute"	            : 'institute',
		"Release Step"		            : 'step',
		"Release Step (CM History)"		: 'step',
		'Institute Name (CM History)'   : 'institute',
		'CM History Id'                 : 'history_id',
		'CM History Record Update Time' : 'history_record_timestamp',
		'Emergency Release Start Date'  : 'er_start_date',
	}
	return df.rename(columns=column_map)

def fill_in_release_date(df):
	assert set(df.columns) >= set(['release_date','release_code','er_start_date'])
	df.ix[df.release_date.isnull() & (df.release_code=='EMERGREL'),'release_date'] = df.ix[df.release_date.isnull() & (df.release_code=='EMERGREL'),'er_start_date']
	return df
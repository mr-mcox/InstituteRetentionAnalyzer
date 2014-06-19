import pandas as pd

def rename_columns(df):		
	column_map = {
		"Person Id"		                : 'pid',
		"First Name"		            : 'first_name',
		"Last Name"		                : 'last_name',
		"Release Code"		            : 'release_code',
		"Release Date"		            : 'release_date',
		"Current Institute"	            : 'institute',
		"Release Step"		            : 'step',
		'Institute Name (CM History)'   : 'institute',
		'CM History Id'                 : 'history_id',
		'CM History Record Update Time' : 'history_record_timestamp',
	}
	return df.rename(columns=column_map)
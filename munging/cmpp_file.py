import pandas as pd

def rename_cmpp_columns(df):		
	column_map = {
		"Person Id"		                                                  : 'pid',
		"First Name"		                                              : 'first_name',
		"Last Name"		                                                  : 'last_name',
		"Status"		                                                  : 'release_code',
		"Date (that CM showed up at institute or that they departed)"	  : 'release_date',
	}
	return df.rename(columns=column_map)

def add_er_pending(df,cmpp_df):
	cmpp = cmpp_df.ix[cmpp_df.release_code=='ER PENDING'].set_index('pid').convert_objects()
	return df.set_index('pid').combine_first(cmpp).reset_index()
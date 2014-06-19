import pandas as pd

def rename_columns(df):		
	column_map = {
		"Person Id"		                                                   : 'pid',
		"Status"		                                                   : 'release_code',
		"Date (that CM showed up at institute or that they departed)"	   : 'release_date',
	}
	return df.rename(columns=column_map)

def add_er_pending(df,cmpp_df):
	return df.set_index('pid').combine_first(cmpp_df.ix[cmpp_df.release_code=='ER PENDING'].set_index('pid')).reset_index()
import pandas as pd

def filter_for_started(df):
	assert 'week' in df.columns
	return df.ix[ (df.week > 0) | (df.week.isnull())]
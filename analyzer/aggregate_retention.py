import pandas as pd

def count_by_release_code(df):
	assert set(df.columns) >= set(['institute','week','release_code','pid'])
	return pd.DataFrame(df.groupby(['institute','week','release_code']).count().rename(columns={'pid':'count'})['count'])

def count_week_zero(df):
	assert set(df.columns) >= set(['institute','pid'])
	return pd.DataFrame({'count':df.groupby('institute').size()})

def fill_extra_weeks(df):
	assert set(df.columns) >= set(['institute','week','release_code','pid'])
	week = pd.DataFrame({'common':[1 for x in range(5)],'week':[x + 1 for x in range(5)]})
	cm_df = pd.DataFrame({'pid':df.pid,'common':[1 for x in range(len(df.index))]})
	df2 = pd.merge(week,cm_df)
	del df2['common']
	# df2 = df2.set_index(['pid','week']).join(df.set_index(['pid','week'])).reset_index()

	return df2
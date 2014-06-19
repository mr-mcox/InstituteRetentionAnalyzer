import pandas as pd
from datetime import datetime, timedelta
import math
import numpy as np

def add_institute_week(df, institute_start_date_df):
	assert 'institute' in df.columns
	assert 'institute' in institute_start_date_df.columns
	assert 'start_date' in institute_start_date_df.columns
	assert 'release_date' in df.columns or 'history_record_timestamp' in df.columns

	df = df.set_index('institute').join(institute_start_date_df.set_index('institute')).reset_index()

	date_column = 'history_record_timestamp'
	if 'release_date' in df.columns:
		date_column = 'release_date'
	df['week'] = (df[date_column] - df.start_date).map( timedelta_to_days )
	del df['start_date']
	return df

def timedelta_to_days(delta):
	if delta == np.datetime64('NaT'):
		return np.NaN
	else:
		return math.floor(delta.astype('timedelta64[D]').item().days/7) + 1
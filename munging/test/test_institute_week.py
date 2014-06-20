from InstituteRetentionAnalyzer.munging.institute_week import *
import pytest
import datetime
import numpy as np

@pytest.fixture
def institute_start_date_df():
	return pd.DataFrame({'institute' : ['Atlanta Institute'],'start_date' : [datetime.datetime(2014,6,1)]})

def test_positive_week(institute_start_date_df):
	df = pd.DataFrame({
						'pid'          : [1],
						'release_date' : [datetime.datetime(2014,6,3)],
						'institute'    : ['Atlanta Institute']
						})
	result = add_institute_week(df, institute_start_date_df)
	assert(result.set_index('pid').loc[1,'week']==1)

def test_negative_week(institute_start_date_df):
	df = pd.DataFrame({
						'pid'          : [1],
						'release_date' : [datetime.datetime(2014,5,25)],
						'institute'    : ['Atlanta Institute']
						})
	result = add_institute_week(df, institute_start_date_df)
	assert(result.set_index('pid').loc[1,'week']<=0)

def test_blank_week(institute_start_date_df):
	df = pd.DataFrame({
						'pid'          : [1,2],
						'release_date' : [np.nan,datetime.datetime(2014,5,25)],
						'institute'    : ['Atlanta Institute','Atlanta Institute']
						})
	result = add_institute_week(df, institute_start_date_df)
	assert(np.isnan(result.set_index('pid').loc[1,'week']))

def test_week_uses_history_timestamp(institute_start_date_df):
	df = pd.DataFrame({
						'pid'          : [1],
						'history_record_timestamp' : [datetime.datetime(2014,6,3,15,2)],
						'institute'    : ['Atlanta Institute']
						})
	result = add_institute_week(df, institute_start_date_df)
	assert(result.set_index('pid').loc[1,'week']==1)

def test_date_to_institute_week(institute_start_date_df):
	date = datetime.datetime(2014,6,9)
	assert date_to_institute_week(institute_start_date_df,'Atlanta Institute', date) == 2
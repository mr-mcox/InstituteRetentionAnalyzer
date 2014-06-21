import pytest
from InstituteRetentionAnalyzer.analyzer.analyzer_for_tpt import TPTRetention
import pandas as pd
from datetime import datetime

@pytest.fixture
def institute_start_date_df():
	return pd.DataFrame({'institute' : ['Atlanta','Chicago','Phoenix'],'start_date' : [datetime(2014,6,1),datetime(2014,6,15),datetime(2014,6,1)]})

@pytest.fixture
def empty_tpt_analyzer():
	return TPTRetention()

@pytest.fixture
def tpt_analyzer_with_institute_transfer():
	#CM 1 transfered from the Atlanta institute in week 4 to week 2 of Chicago. CM 2 completed all 5 weeks in Chicago
	analyzer = TPTRetention()
	analyzer.cm_history_cleaned = pd.DataFrame({
								'pid'                         : [1,1,1,2],
								'week'                        : [4,2,2,3],
								'history_id'                  : [1,2,3,4],
								'institute'                   : ['Atlanta','Chicago','Chicago','Chicago'],
								'is_notable_institute_record' : [True,True,False,False],
								'is_first_institute'          : [True,False,False,True],
								'is_transfer_out'             : [True,False,False,False],
								'is_transfer_in'              : [False,True,False,False],

								})
	analyzer.exit_data_cleaned = pd.DataFrame({
							'pid'  : [1,2],
							'week' : [None,None],
							'institute': ['Chicago','Chicago'],
							'release_code' : [None,None]
							})

	return analyzer

@pytest.fixture
def tpt_analyzer_with_institute_transfer_and_resignation():
	#CM 1 transfered from the Atlanta institute in week 4 to week 2 of Chicago then resigned in week 4. CM 2 started in Chicago and resigned in week 4
	analyzer = TPTRetention()
	analyzer.cm_history_cleaned = pd.DataFrame({
								'pid'                         : [1,1,1,2],
								'week'                        : [4,2,2,3],
								'history_id'                  : [1,2,3,4],
								'institute'                   : ['Atlanta','Chicago','Chicago','Chicago'],
								'is_notable_institute_record' : [True,True,False,False],
								'is_first_institute'          : [True,False,False,True],
								'is_transfer_out'             : [True,False,False,False],
								'is_transfer_in'              : [False,True,False,False],

								})
	analyzer.exit_data_cleaned = pd.DataFrame({
								'pid'  : [1,2],
								'week' : [4,4],
								'institute': ['Chicago','Chicago'],
								'release_code' : ['RESIGNED','RESIGNED']
								})
	return analyzer

@pytest.fixture
def tpt_analyzer_with_one_cm_transfer(institute_start_date_df):
	analyzer = TPTRetention()
	analyzer.institute_start_date_df = institute_start_date_df
	analyzer.cm_history_cleaned = pd.DataFrame({
									'pid'                      : [1,1,1],
									'week'                     : [1,2,2],
									'history_record_timestamp' : [datetime(2014,6,1),datetime(2014,6,23),datetime(2014,6,25)],
									'history_id'               : [1,2,3],
									'institute'                : ['Atlanta','Chicago','Chicago'],
									})
	return analyzer

@pytest.fixture
def tpt_analyzer_with_cm_boundary():
	analyzer = TPTRetention()
	boundary_records = [
		(1,'Atlanta',0,4),
		(1,'Chicago',2,3),
		(2,'Chicago',0,5),
	]
	analyzer.cm_institute_boundaries = pd.DataFrame.from_records(boundary_records,columns=['pid','institute','start_week','end_week'])
	return analyzer

def test_exit_by_institute_and_week(empty_tpt_analyzer):
		analyzer = empty_tpt_analyzer
		analyzer.exit_data_cleaned = pd.DataFrame({
										'pid'  : [1,2,3],
										'week' : [1,2,2],
										'institute': ['Chicago','Atlanta','Atlanta'],
										'release_code' : ['RESIGNED','RESIGNED','RESIGNED',]
										})
		analyzer.count_by_release_code()
		assert(analyzer.release_code_count_by_institute_week.loc[('Chicago',1,'RESIGNED'),'count']==1)
		assert(analyzer.release_code_count_by_institute_week.loc[('Atlanta',2,'RESIGNED'),'count']==2)

def test_fill_extra_weeks(empty_tpt_analyzer):
		df = pd.DataFrame({
			'pid'  : [1,2,3],
			'week' : [None,1,2],
			'institute': ['Atlanta','Atlanta','Atlanta'],
			'release_code' : [None,'RESIGNED','RESIGNED',]
			})
		result = empty_tpt_analyzer.fill_extra_weeks(df)
		assert(len(result.ix[(result.pid == 1) & (result.week ==1)].index)>=1)
		assert(len(result.ix[(result.pid == 2) & (result.week ==1)].index)>=1)

def test_mark_notable_institute_assignment_records_for_one_cm(tpt_analyzer_with_one_cm_transfer):
	analyzer = tpt_analyzer_with_one_cm_transfer
	analyzer.mark_notable_institute_assignment_records()
	df = analyzer.cm_history_cleaned.set_index(['pid','history_id']).sortlevel()
	assert(df.loc[(1,1),'is_notable_institute_record'])
	assert(df.loc[(1,2),'is_notable_institute_record'])
	assert( not df.loc[(1,3),'is_notable_institute_record'])

def test_mark_notable_institute_assignment_records_for_multiple_cms(empty_tpt_analyzer, institute_start_date_df):
	analyzer = empty_tpt_analyzer
	analyzer.institute_start_date_df = institute_start_date_df
	analyzer.cm_history_cleaned = pd.DataFrame({
									'pid'        : [1,1,2],
									'week'       : [1,2,2],
									'history_id' : [1,2,3],
									'history_record_timestamp' : [datetime(2014,6,1),datetime(2014,6,1),datetime(2014,6,1)],
									'institute'  : ['Chicago','Atlanta','Phoenix'],
									})
	analyzer.mark_notable_institute_assignment_records()
	df = analyzer.cm_history_cleaned.set_index(['pid','history_id']).sortlevel()
	assert(df.loc[(1,1),'is_notable_institute_record'])
	assert(df.loc[(1,2),'is_notable_institute_record'])
	assert( not df.loc[(2,3),'is_notable_institute_record'])

def test_mark_transfer_in(tpt_analyzer_with_one_cm_transfer):
	analyzer = tpt_analyzer_with_one_cm_transfer
	analyzer.mark_notable_institute_assignment_records()
	df = analyzer.cm_history_cleaned.set_index(['pid','history_id']).sortlevel()
	assert(not df.loc[(1,1),'is_transfer_in'])
	assert(df.loc[(1,2),'is_transfer_in'])

def test_mark_transfer_out(tpt_analyzer_with_one_cm_transfer):
	analyzer = tpt_analyzer_with_one_cm_transfer
	analyzer.mark_notable_institute_assignment_records()
	df = analyzer.cm_history_cleaned.set_index(['pid','history_id']).sortlevel()
	assert(df.loc[(1,1),'is_transfer_out'])
	assert( not df.loc[(1,2),'is_transfer_out'])

def test_mark_transfer_out_with_modified_week(tpt_analyzer_with_one_cm_transfer):
	analyzer = tpt_analyzer_with_one_cm_transfer
	analyzer.mark_notable_institute_assignment_records()
	df = analyzer.cm_history_cleaned.set_index(['pid','history_id']).sortlevel()
	assert(df.loc[(1,1),'week']==4)


def test_count_transfer_in_by_institute_week(tpt_analyzer_with_one_cm_transfer):
	analyzer = tpt_analyzer_with_one_cm_transfer
	analyzer.mark_notable_institute_assignment_records()
	analyzer.count_transfers()
	assert(analyzer.transfer_in_count_by_institute_week.loc[('Chicago',2),'count']==1)

def test_count_transfer_out_by_institute_week(tpt_analyzer_with_one_cm_transfer):
	analyzer = tpt_analyzer_with_one_cm_transfer
	analyzer.mark_notable_institute_assignment_records()
	analyzer.count_transfers()
	assert(analyzer.transfer_out_count_by_institute_week.loc[('Atlanta',4),'count']==1)

def test_mark_first_institute_of_record(empty_tpt_analyzer,institute_start_date_df):
	analyzer = empty_tpt_analyzer
	analyzer.institute_start_date_df = institute_start_date_df
	analyzer.cm_history_cleaned = pd.DataFrame({
									'pid'        : [1,1,1,2],
									'week'       : [-1,2,2,1],
									'history_id' : [1,2,3,4],
									'history_record_timestamp' : [datetime(2014,6,1),datetime(2014,6,1),datetime(2014,6,1),datetime(2014,6,1)],
									'institute'  : ['Chicago','Atlanta','Atlanta','Atlanta'],
									})
	analyzer.mark_notable_institute_assignment_records()
	df = analyzer.cm_history_cleaned.set_index(['pid','history_id']).sortlevel()
	assert(df.loc[(1,2),'is_first_institute'])
	assert(df.loc[(2,4),'is_first_institute'])
	assert(len(df.ix[df.is_first_institute].index)==2)

def test_useful_institute_records(tpt_analyzer_with_institute_transfer):
	analyzer = tpt_analyzer_with_institute_transfer
	analyzer.find_useful_institute_records()
	df = analyzer.useful_institute_records.set_index(['pid','week']).sortlevel()
	assert(df.loc[(1,2),'institute']=="Chicago")
	assert(df.loc[(1,4),'institute']=="Atlanta")
	assert(df.loc[(2,3),'institute']=="Chicago")

def test_cm_institute_boundaries_with_first_record_transfer_out(tpt_analyzer_with_institute_transfer):
	analyzer = tpt_analyzer_with_institute_transfer
	analyzer.create_cm_institute_boundaries()
	df = analyzer.cm_institute_boundaries
	df = df.set_index(['pid','institute','start_week','end_week'])
	assert(df.index.isin([(1,'Atlanta',0,3)]).sum()==1)

def test_cm_institute_boundaries_with_transfer_in(tpt_analyzer_with_institute_transfer):
	analyzer = tpt_analyzer_with_institute_transfer
	analyzer.create_cm_institute_boundaries()
	df = analyzer.cm_institute_boundaries
	df = df.set_index(['pid','institute','start_week','end_week'])
	print(df)
	assert(df.index.isin([(1,'Chicago',2,5)]).sum()==1)

def test_cm_institute_boundaries_for_normal(tpt_analyzer_with_institute_transfer):
	analyzer = tpt_analyzer_with_institute_transfer
	analyzer.create_cm_institute_boundaries()
	df = analyzer.cm_institute_boundaries
	df = df.set_index(['pid','institute','start_week','end_week'])
	print(df)
	assert(df.index.isin([(2,'Chicago',0,5)]).sum()==1)

def test_cm_institute_boundaries_for_resignation(tpt_analyzer_with_institute_transfer_and_resignation):
	analyzer = tpt_analyzer_with_institute_transfer_and_resignation
	analyzer.create_cm_institute_boundaries()
	df = analyzer.cm_institute_boundaries
	df = df.set_index(['pid','institute','start_week','end_week'])
	print(df)
	assert(df.index.isin([(2,'Chicago',0,3)]).sum()==1)

def test_cm_institute_boundaries_for_transfer_and_resignation(tpt_analyzer_with_institute_transfer_and_resignation):
	analyzer = tpt_analyzer_with_institute_transfer_and_resignation
	analyzer.create_cm_institute_boundaries()
	df = analyzer.cm_institute_boundaries
	df = df.set_index(['pid','institute','start_week','end_week'])
	print(df)
	assert(df.index.isin([(1,'Atlanta',0,3)]).sum()==1)
	assert(df.index.isin([(1,'Chicago',2,3)]).sum()==1)

def test_create_weeks_active(tpt_analyzer_with_cm_boundary):
	analyzer = tpt_analyzer_with_cm_boundary
	analyzer.create_active_cms_by_week()
	df = analyzer.active_cms_by_week.set_index(['pid','institute']).sortlevel()
	print(df)
	assert(df.index.isin([(1,'Atlanta')]).sum()==5)
	assert(df.index.isin([(1,'Chicago')]).sum()==2)
	assert(df.index.isin([(2,'Chicago')]).sum()==6)
	df = analyzer.active_cms_by_week.set_index(['pid','institute','week']).sortlevel()
	assert(df.index.isin([(1,'Atlanta',0)]).sum()==1)
	assert(df.index.isin([(1,'Atlanta',4)]).sum()==1)


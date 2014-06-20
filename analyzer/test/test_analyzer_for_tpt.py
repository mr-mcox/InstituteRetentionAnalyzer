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
def tpt_analyzer_with_institute_transfer_and_resignation():
	#CM 1 transfered from the Atlanta to Phoenix institutes then resigned a week later. CM 2 is currently active in Phoenix 
	analyzer = TPTRetention()
	analyzer.cm_history_cleaned = pd.DataFrame({
								'pid'                         : [1,1,1,2],
								'week'                        : [2,1,2,3],
								'history_id'                  : [1,2,3,4],
								'institute'                   : ['Atlanta','Phoenix','Phoenix','Phoenix'],
								'is_notable_institute_record' : [True,True,False,False],
								'is_first_institute'          : [True,False,False,True],
								})
	analyzer.exit_data_cleaned = pd.DataFrame({
								'pid'  : [1,2],
								'week' : [3,3],
								'institute': ['Phoenix','Phoenix'],
								'release_code' : ['RESIGNED',None]
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

def test_assign_significant_institutes(tpt_analyzer_with_institute_transfer_and_resignation):
	analyzer = tpt_analyzer_with_institute_transfer_and_resignation
	analyzer.create_all_weeks_data()
	df = analyzer.all_weeks_data.set_index(['pid','week']).sortlevel()
	assert(df.loc[(1,1),'institute']=="Phoenix")
	assert(df.loc[(1,2),'institute']=="Atlanta")
	assert(df.loc[(2,3),'institute']=="Phoenix")

# def test_fill_in_weeks_for_institutes(tpt_analyzer_with_institute_transfer_and_resignation):
# 	analyzer = tpt_analyzer_with_institute_transfer_and_resignation
# 	analyzer.create_all_weeks_data()
# 	df = analyzer.all_weeks_data.set_index(['pid','institute','week']).sortlevel()
# 	assert(df.index.isin([(1,'Atlanta',1)]).sum()==1)
# 	assert(df.index.isin([(1,'Atlanta',2)]).sum()==1)
# 	assert(df.index.isin([(1,'Atlanta',3)]).sum()==0)
# 	assert(df.index.isin([(1,'Phoenix',1)]).sum()==1)
# 	assert(df.index.isin([(1,'Phoenix',3)]).sum()==1)


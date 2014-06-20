import pytest
from InstituteRetentionAnalyzer.analyzer.analyzer_for_tpt import TPTRetention
import pandas as pd

@pytest.fixture
def empty_tpt_analyzer():
	return TPTRetention()

def test_exit_by_institute_and_week(empty_tpt_analyzer):
		analyzer = empty_tpt_analyzer
		analyzer.exit_data_cleaned = pd.DataFrame({
										'pid'  : [1,2,3],
										'week' : [1,2,2],
										'institute': ['Chicago','Atlanta','Atlanta'],
										'release_code' : ['RESIGNED','RESIGNED','RESIGNED',]
										})
		analyzer.count_by_release_code()
		assert(analyzer.release_code_count.loc[('Chicago',1,'RESIGNED'),'count']==1)
		assert(analyzer.release_code_count.loc[('Atlanta',2,'RESIGNED'),'count']==2)

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

def test_mark_notable_institute_assignment_records_for_one_cm(empty_tpt_analyzer):
	analyzer = empty_tpt_analyzer
	analyzer.cm_history_cleaned = pd.DataFrame({
									'pid'        : [1,1,1],
									'week'       : [1,2,2],
									'history_id' : [1,2,3],
									'institute'  : ['Chicago','Atlanta','Atlanta'],
									})
	analyzer.mark_notable_institute_assignment_records()
	df = analyzer.cm_history_cleaned.set_index(['pid','history_id']).sortlevel()
	assert(df.loc[(1,1),'is_notable_institute_record'])
	assert(df.loc[(1,2),'is_notable_institute_record'])
	assert( not df.loc[(1,3),'is_notable_institute_record'])

def test_mark_notable_institute_assignment_records_for_multiple_cms(empty_tpt_analyzer):
	analyzer = empty_tpt_analyzer
	analyzer.cm_history_cleaned = pd.DataFrame({
									'pid'        : [1,1,2],
									'week'       : [1,2,2],
									'history_id' : [1,2,3],
									'institute'  : ['Chicago','Atlanta','Phoenix'],
									})
	analyzer.mark_notable_institute_assignment_records()
	df = analyzer.cm_history_cleaned.set_index(['pid','history_id']).sortlevel()
	assert(df.loc[(1,1),'is_notable_institute_record'])
	assert(df.loc[(1,2),'is_notable_institute_record'])
	assert( not df.loc[(2,3),'is_notable_institute_record'])

def test_mark_transfer_in(empty_tpt_analyzer):
	analyzer = empty_tpt_analyzer
	analyzer.cm_history_cleaned = pd.DataFrame({
									'pid'        : [1,1,1],
									'week'       : [1,2,2],
									'history_id' : [1,2,3],
									'institute'  : ['Chicago','Atlanta','Atlanta'],
									})
	analyzer.mark_notable_institute_assignment_records()
	df = analyzer.cm_history_cleaned.set_index(['pid','history_id']).sortlevel()
	assert(not df.loc[(1,1),'is_transfer_in'])
	assert(df.loc[(1,2),'is_transfer_in'])

def test_mark_transfer_out(empty_tpt_analyzer):
	analyzer = empty_tpt_analyzer
	analyzer.cm_history_cleaned = pd.DataFrame({
									'pid'        : [1,1,1],
									'week'       : [1,2,2],
									'history_id' : [1,2,3],
									'institute'  : ['Chicago','Atlanta','Atlanta'],
									})
	analyzer.mark_notable_institute_assignment_records()
	df = analyzer.cm_history_cleaned.set_index(['pid','history_id']).sortlevel()
	assert(df.loc[(1,1),'is_transfer_out'])
	assert( not df.loc[(1,2),'is_transfer_out'])

def test_count_transfer_in_by_institute_week(empty_tpt_analyzer):
	analyzer = empty_tpt_analyzer
	analyzer.cm_history_cleaned = pd.DataFrame({
									'pid'        : [1,1,1],
									'week'       : [1,2,2],
									'history_id' : [1,2,3],
									'institute'  : ['Chicago','Atlanta','Atlanta'],
									})
	analyzer.mark_notable_institute_assignment_records()
	analyzer.count_transfers()
	assert(analyzer.transfer_in_count_by_institute_week.loc[('Atlanta',2),'count']==1)

def test_count_transfer_out_by_institute_week(empty_tpt_analyzer):
	analyzer = empty_tpt_analyzer
	analyzer.cm_history_cleaned = pd.DataFrame({
									'pid'        : [1,1,1],
									'week'       : [1,2,2],
									'history_id' : [1,2,3],
									'institute'  : ['Chicago','Atlanta','Atlanta'],
									})
	analyzer.mark_notable_institute_assignment_records()
	analyzer.count_transfers()
	assert(analyzer.transfer_out_count_by_institute_week.loc[('Chicago',1),'count']==1)


 



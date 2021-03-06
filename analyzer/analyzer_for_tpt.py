import pandas as pd
from InstituteRetentionAnalyzer.munging.institute_week import *
from InstituteRetentionAnalyzer.munging.cmpp_file import *
from InstituteRetentionAnalyzer.munging.reformat_bobj import *
from InstituteRetentionAnalyzer.analyzer.filter import filter_for_started


class TPTRetention(object):
	"""docstring for TPTRetention"""
	def __init__(self, **kwargs):
		exit_data_cleaned       = kwargs.pop('exit_data_cleaned',None)
		cmpp_data_cleaned       = kwargs.pop('cmpp_data_cleaned',None)
		cm_history_cleaned      = kwargs.pop('cm_history_cleaned',None)
		institute_start_date_df = kwargs.pop('institute_start_date_df',None)

		if cmpp_data_cleaned is not None:
			exit_data_cleaned = add_er_pending(exit_data_cleaned,cmpp_data_cleaned)

		if exit_data_cleaned is not None:
			assert 'release_code' in exit_data_cleaned.columns
			exit_data_cleaned = exit_data_cleaned.ix[~((exit_data_cleaned.release_code=="NOSHOW")|(exit_data_cleaned.release_code=="DEFERRED"))]
			if 'week' not in exit_data_cleaned.columns:
				exit_data_cleaned = fill_in_release_date(exit_data_cleaned)
				exit_data_cleaned = add_institute_week(exit_data_cleaned,institute_start_date_df)
				exit_data_cleaned = filter_for_started(exit_data_cleaned)
				exit_data_cleaned = exit_data_cleaned.ix[exit_data_cleaned.institute.isin(institute_start_date_df.institute)]

		if cm_history_cleaned is not None:
			if 'step' in cm_history_cleaned.columns:
				#Remove CMs without step to not take into account records before CMs reached pre-inst
				cm_history_cleaned = cm_history_cleaned.ix[cm_history_cleaned.step.notnull()]
			if exit_data_cleaned is not None:
				cm_history_cleaned = cm_history_cleaned.ix[cm_history_cleaned.pid.isin(exit_data_cleaned.pid)]
			if 'week' not in cm_history_cleaned.columns:
				cm_history_cleaned = add_institute_week(cm_history_cleaned,institute_start_date_df)
				if exit_data_cleaned is not None and 'step' in cm_history_cleaned.columns:
					all_cms = pd.Series(cm_history_cleaned.pid.unique())
					cms_without_any_data_while_institute_in_session = all_cms.ix[~all_cms.isin(cm_history_cleaned.ix[cm_history_cleaned.week > 0,'pid'])]
					cm_history_cleaned.ix[cm_history_cleaned.pid.isin(cms_without_any_data_while_institute_in_session) & cm_history_cleaned.pid.isin(exit_data_cleaned.pid) & (cm_history_cleaned.step=='INSTREG') & (cm_history_cleaned.week > -10),'week']=1
				cm_history_cleaned = filter_for_started(cm_history_cleaned)
				cm_history_cleaned = cm_history_cleaned.ix[cm_history_cleaned.institute.isin(institute_start_date_df.institute)]

		self.exit_data_cleaned       = exit_data_cleaned
		self.cm_history_cleaned      = cm_history_cleaned
		self.institute_start_date_df = institute_start_date_df

	def count_by_release_code(self):
		assert hasattr(self,'exit_data_cleaned') and self.exit_data_cleaned is not None
		assert set(self.exit_data_cleaned.columns) >= set(['institute','week','release_code','pid'])
		self.release_code_count_by_institute_week = pd.DataFrame(self.exit_data_cleaned.groupby(['institute','week','release_code']).count().rename(columns={'pid':'count'})['count'])
		self.list_of_exited_cms = self.exit_data_cleaned.ix[self.exit_data_cleaned.release_code.notnull(),['pid','first_name','last_name','institute','release_code','release_date','week']].sort(['institute','week','release_code'])
		return self

	def fill_extra_weeks(self, df):
		assert set(df.columns) >= set(['institute','week','release_code','pid'])
		week = pd.DataFrame({'common':[1 for x in range(5)],'week':[x + 1 for x in range(5)]})
		cm_df = pd.DataFrame({'pid':df.pid,'common':[1 for x in range(len(df.index))]})
		df2 = pd.merge(week,cm_df)
		del df2['common']

		return df2

	def mark_notable_institute_assignment_records(self):
		assert hasattr(self,'cm_history_cleaned') and self.cm_history_cleaned is not None
		assert hasattr(self,'institute_start_date_df') and self.institute_start_date_df is not None
		assert set(self.cm_history_cleaned.columns) >= set(['institute','week','history_id','pid','history_record_timestamp'])
		self.cm_history_cleaned['is_notable_institute_record'] = False
		self.cm_history_cleaned['is_transfer_in'] = False
		self.cm_history_cleaned['is_transfer_out'] = False
		self.cm_history_cleaned['is_first_institute'] = False
		df = self.cm_history_cleaned.set_index(['pid','history_id']).sortlevel()
		previous_index = None
		previous_institute = None
		previous_pid = None
		previous_week = None
		for i in df.index:
			current_institute = df.loc[i]['institute']
			current_pid, current_hist_id = i
			current_week = df.loc[i]['week']

			#Mark first institutes
			if (previous_pid != current_pid and current_week >= 1) or (previous_week is not None and previous_week < 1):
				df.at[i,'is_first_institute'] = True

			#Check whether we're looking at a new cm, reset institute
			if previous_pid is not None and current_pid != previous_pid:
				previous_institute = None
				previous_week = None

			#Mark transfers
			if previous_institute is not None and current_institute != previous_institute:
				df.at[previous_index,'is_notable_institute_record'] = True
				df.at[previous_index,'is_transfer_out'] = True
				df.at[previous_index,'week'] = date_to_institute_week(self.institute_start_date_df,df.at[previous_index,'institute'],df.at[i,'history_record_timestamp'])
				df.at[i,'is_notable_institute_record'] = True
				df.at[i,'is_transfer_in'] = True
			previous_index = i
			previous_institute = current_institute
			previous_pid = current_pid
			previous_week = current_week
		# df = pd.DataFrame(df.reset_index, columns = [['institute','week','history_id','pid','is_notable_institute_record','is_transfer_out','is_transfer_in'])
		self.cm_history_cleaned = df.reset_index()

	def count_transfers(self):
		assert hasattr(self,'cm_history_cleaned') and self.cm_history_cleaned is not None
		if 'is_transfer_in' not in self.cm_history_cleaned:
			self.mark_notable_institute_assignment_records()
		self.transfer_in_count_by_institute_week = pd.DataFrame({'count':self.cm_history_cleaned.ix[self.cm_history_cleaned.is_transfer_in].groupby(['institute','week']).size()})
		self.transfer_out_count_by_institute_week = pd.DataFrame({'count':self.cm_history_cleaned.ix[self.cm_history_cleaned.is_transfer_out].groupby(['institute','week']).size()})
		df = self.cm_history_cleaned.copy()
		transfer_out_cms = df.ix[df.is_transfer_out,['pid','first_name','last_name','institute','week']]
		transfer_in_cms = df.ix[df.is_transfer_in,['pid','first_name','last_name','institute','week']]
		transfer_out_cms['transfer_type'] = 'transfer_out'
		transfer_in_cms['transfer_type'] = 'transfer_in'
		self.list_of_transfer_cms = pd.concat([transfer_out_cms,transfer_in_cms]).sort(['institute','week','transfer_type'])
		return self

	def find_useful_institute_records(self):
		assert hasattr(self,'cm_history_cleaned') and self.cm_history_cleaned is not None
		if 'is_first_institute' not in self.cm_history_cleaned:
			self.mark_notable_institute_assignment_records()

		self.useful_institute_records = self.cm_history_cleaned.ix[self.cm_history_cleaned.is_first_institute | self.cm_history_cleaned.is_notable_institute_record]
		return self

	def create_cm_institute_boundaries(self):
		assert hasattr(self,'exit_data_cleaned') and self.exit_data_cleaned is not None
		if not hasattr(self,'useful_institute_records') or self.useful_institute_records is None:
			self.find_useful_institute_records()
		assert set(self.useful_institute_records.columns) >= set(['pid','history_id','institute','week','is_first_institute','is_transfer_in','is_transfer_out'])
		exit_records = self.exit_data_cleaned
		df = self.useful_institute_records.set_index(['pid','history_id']).sortlevel()

		boundary_records = list()
		index_i = 0
		# are_within_CM = False
		while(index_i <= (len(df.index)-1)):
			next_index_delta = 1
			cur_index = df.index[index_i]
			create_record = True
			current_institute = df.loc[cur_index,'institute']
			current_pid, current_hist_id = df.index[index_i]
			start_week = 0
			end_week = 7

			next_pid = None
			next_hist_id = None
			if index_i < (len(df.index)-1):
				next_index = df.index[index_i + 1]
				next_pid, next_hist_id = next_index
			if not df.loc[cur_index,'is_first_institute']:
				start_week = df.loc[cur_index,'week']
			if next_pid == current_pid:
				if df.loc[next_index,'institute'] == current_institute and df.loc[cur_index,'is_first_institute']:
					df.at[cur_index,'is_first_institute'] = False
					df.at[next_index,'is_first_institute'] = True
					create_record = False
				if df.loc[cur_index,'is_transfer_out']:
					# next_index_delta = 2
					end_week = df.loc[cur_index,'week'] - 1
				else:
					df2 = df.reset_index()
					if create_record:
						assert False, 'When processing id ' + str(current_hist_id) + ' Somehow there are multiple CM records in a row without a transfer: ' + str(df2.ix[df2.pid == current_pid,:])
			if create_record:
				if len(exit_records.ix[(exit_records.pid == current_pid) & (exit_records.institute == current_institute) & exit_records.release_code.notnull()].index == 1):
					end_week = exit_records.ix[(exit_records.pid == current_pid) & (exit_records.institute == current_institute) & exit_records.release_code.notnull(),'week'].iloc[0] -1
				boundary_records.append((current_pid,current_institute,start_week,end_week))
			index_i += next_index_delta
		self.cm_institute_boundaries = pd.DataFrame.from_records(boundary_records, columns =['pid','institute','start_week','end_week'])
		return self

	def create_active_cms_by_week(self):
		if not hasattr(self,'cm_institute_boundaries') or self.cm_institute_boundaries is None:
			self.create_cm_institute_boundaries()
		all_cm_records = []
		df = self.cm_institute_boundaries
		for idx in df.index:
			start_week = int(df.loc[idx,'start_week'])
			end_week = int(df.loc[idx,'end_week'])
			all_cm_records = all_cm_records + [(df.loc[idx,'pid'], df.loc[idx,'institute'],week + start_week) for week in range(end_week - start_week + 1)]
		self.active_cms_by_week = pd.DataFrame.from_records(all_cm_records,columns=['pid','institute','week'])
		return self

	def count_active_cms_by_week(self):
		if not hasattr(self,'active_cms_by_week') or self.active_cms_by_week is None:
			self.create_active_cms_by_week()
		national_df= self.active_cms_by_week.copy()
		national_df['institute'] = "National"
		institute_count = pd.DataFrame(self.active_cms_by_week.groupby(['institute','week']).count().rename(columns={'pid':'count'})['count'])
		national_count = pd.DataFrame(national_df.groupby(['institute','week']).count().rename(columns={'pid':'count'})['count'])
		self.count_of_active_cms_by_week = pd.concat([institute_count,national_count])
		if hasattr(self,'cm_history_cleaned') and self.cm_history_cleaned is not None:
			self.list_of_week_0_cms = self.active_cms_by_week.ix[self.active_cms_by_week.week==0,['pid','institute']].set_index('pid').join(self.cm_history_cleaned.ix[:,['pid','first_name','last_name']].drop_duplicates().set_index('pid')).reset_index()
		return self

	def compute_percent_active_by_week(self):
		if not hasattr(self,'count_of_active_cms_by_week') or self.count_of_active_cms_by_week is None:
			self.count_active_cms_by_week()
		df = self.count_of_active_cms_by_week.reset_index().set_index('institute')
		wk0 = df.ix[df.week==0].rename(columns={'count':'wk0_count'})
		del wk0['week']
		df = df.join(wk0)
		df['value'] = df['count']/df.wk0_count
		df = df.reset_index()
		self.percent_active_by_week = pd.DataFrame(df,columns=['institute','week','value']).set_index(['institute','week'])

		return self

	def create_formatted_table(self):
		if not hasattr(self,'transfer_in_count_by_institute_week') or self.transfer_in_count_by_institute_week is None or not hasattr(self,'transfer_out_count_by_institute_week') or self.transfer_out_count_by_institute_week is None:
			self.count_transfers()
		if not hasattr(self,'release_code_count_by_institute_week') or self.release_code_count_by_institute_week is None:
			self.count_by_release_code()
		if not hasattr(self,'count_of_active_cms_by_week') or self.count_of_active_cms_by_week is None:
			self.count_active_cms_by_week()
		if not hasattr(self,'percent_active_by_week') or self.percent_active_by_week is None:
			self.compute_percent_active_by_week()
		transfer_in_count = self.transfer_in_count_by_institute_week.reset_index().rename(columns={'count':'value'})
		transfer_in_count['value_type'] = 'transfer_in_count'
		transfer_out_count = self.transfer_out_count_by_institute_week.reset_index().rename(columns={'count':'value'})
		transfer_out_count['value_type'] = 'transfer_out_count'
		release_code_count = self.release_code_count_by_institute_week.reset_index().rename(columns={'count':'value','release_code':'value_type'})
		active_count = self.count_of_active_cms_by_week.reset_index().rename(columns={'count':'value'})
		active_count['value_type'] = 'active_count'
		active_percent = self.percent_active_by_week.reset_index()
		active_percent['value_type'] = 'active_percent'
		df = pd.concat([transfer_in_count,transfer_out_count,release_code_count,active_count,active_percent])
		if 'index' in df.columns:
			del df['index']
		df = df.set_index(['institute','value_type','week'])
		df = df.unstack()
		df = df.reset_index()
		value_type_order_map = {
			"active_percent"     : 1,
			"active_count"       : 2,
			"RESIGNED"           : 3,
			"ER PENDING"         : 4,
			"EMERGREL"           : 5,
			"TERMINATED"         : 6,
			'transfer_out_count' : 7,
			'transfer_in_count'  : 8,
		}
		df['value_order'] = df.value_type.map(value_type_order_map)
		df = df.set_index(['institute','value_order','value_type']).sortlevel()
		self.formated_retention_table = df
		return self






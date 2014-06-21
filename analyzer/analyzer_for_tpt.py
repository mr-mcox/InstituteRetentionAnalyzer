import pandas as pd
from InstituteRetentionAnalyzer.munging.institute_week import *
import pdb

class TPTRetention(object):
	"""docstring for TPTRetention"""
	def __init__(self, **kwargs):
		pass

	def count_by_release_code(self):
		assert hasattr(self,'exit_data_cleaned')
		assert set(self.exit_data_cleaned.columns) >= set(['institute','week','release_code','pid'])
		self.release_code_count_by_institute_week = pd.DataFrame(self.exit_data_cleaned.groupby(['institute','week','release_code']).count().rename(columns={'pid':'count'})['count'])
		return self

	def fill_extra_weeks(self, df):
		assert set(df.columns) >= set(['institute','week','release_code','pid'])
		week = pd.DataFrame({'common':[1 for x in range(5)],'week':[x + 1 for x in range(5)]})
		cm_df = pd.DataFrame({'pid':df.pid,'common':[1 for x in range(len(df.index))]})
		df2 = pd.merge(week,cm_df)
		del df2['common']

		return df2

	def mark_notable_institute_assignment_records(self):
		assert hasattr(self,'cm_history_cleaned')
		assert hasattr(self,'institute_start_date_df')
		assert set(self.cm_history_cleaned.columns) >= set(['institute','week','history_id','pid','history_record_timestamp'])
		self.cm_history_cleaned['is_notable_institute_record'] = False
		self.cm_history_cleaned['is_transfer_in'] = False
		self.cm_history_cleaned['is_transfer_out'] = False
		self.cm_history_cleaned['is_first_institute'] = False
		df = self.cm_history_cleaned.set_index(['pid','history_id'])
		previous_index = None
		previous_institute = None
		previous_pid = None
		previous_week = None
		for i in df.index:
			current_institute = df.loc[i,'institute']
			current_pid, current_hist_id = i
			current_week = df.loc[i,'week']

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
		self.cm_history_cleaned = df.reset_index()

	def count_transfers(self):
		assert hasattr(self,'cm_history_cleaned')
		if 'is_transfer_in' not in self.cm_history_cleaned:
			self.mark_notable_institute_assignment_records()
		self.transfer_in_count_by_institute_week = pd.DataFrame({'count':self.cm_history_cleaned.ix[self.cm_history_cleaned.is_transfer_in].groupby(['institute','week']).size()})
		self.transfer_out_count_by_institute_week = pd.DataFrame({'count':self.cm_history_cleaned.ix[self.cm_history_cleaned.is_transfer_out].groupby(['institute','week']).size()})
		return self

	def find_useful_institute_records(self):
		assert hasattr(self,'cm_history_cleaned')
		if 'is_first_institute' not in self.cm_history_cleaned:
			self.mark_notable_institute_assignment_records()

		self.useful_institute_records = self.cm_history_cleaned.ix[self.cm_history_cleaned.is_first_institute | self.cm_history_cleaned.is_notable_institute_record]
		return self

	def create_cm_institute_boundaries(self):
		assert hasattr(self,'exit_data_cleaned')
		if not hasattr(self,'useful_institute_records'):
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
			current_institute = df.loc[cur_index,'institute']
			current_pid, current_hist_id = df.index[index_i]
			start_week = 0
			if not df.loc[cur_index,'is_first_institute']:
				start_week = df.loc[cur_index,'week']
			end_week = 5

			next_pid = None
			next_hist_id = None
			if index_i < (len(df.index)-1):
				next_pid, next_hist_id = df.index[index_i + 1]
			if next_pid == current_pid:
				if df.loc[cur_index,'is_transfer_out']:
					# next_index_delta = 2
					end_week = df.loc[cur_index,'week'] - 1
				else:
					df2 = df.reset_index()
					assert False, 'Somehow there are multiple CM records in a row without a transfer: ' + str(df2.ix[df2.pid == current_pid,:])
			if len(exit_records.ix[(exit_records.pid == current_pid) & (exit_records.institute == current_institute) & exit_records.release_code.notnull()].index == 1):
				end_week = exit_records.ix[(exit_records.pid == current_pid) & (exit_records.institute == current_institute) & exit_records.release_code.notnull(),'week'].iloc[0] -1
			boundary_records.append((current_pid,current_institute,start_week,end_week))
			index_i += next_index_delta
		self.cm_institute_boundaries = pd.DataFrame.from_records(boundary_records, columns =['pid','institute','start_week','end_week'])
		return self

	def create_active_cms_by_week(self):
		if not hasattr(self,'cm_institute_boundaries'):
			self.create_cm_institute_boundaries()
		all_cm_records = []
		df = self.cm_institute_boundaries
		for idx in df.index:
			all_cm_records = all_cm_records + [(df.loc[idx,'pid'], df.loc[idx,'institute'],week + df.loc[idx,'start_week']) for week in range(df.loc[idx,'end_week'] - df.loc[idx,'start_week'] + 1)]
		self.active_cms_by_week = pd.DataFrame.from_records(all_cm_records,columns=['pid','institute','week'])

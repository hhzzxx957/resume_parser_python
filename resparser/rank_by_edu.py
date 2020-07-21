# -*- coding: utf-8 -*-
'''
Building a class to rank multiple resumes by education (the rank of university).
'''
from os import listdir
import time
import multiprocessing as mp
from functools import partial
import pandas as pd
from .resume_parser import ResumeParser
# from .utils import timer

class ResumeRank(object):
    '''
    Main class for ranking.
    '''

    def __init__(self, res_path='./resume/', multiproc=True):
        self.path = res_path
        manager = mp.Manager()
        self.multiproc = multiproc
        if self.multiproc:
            self.res_dic = {
                'file name': manager.list(),
                'highest degree': manager.list(),
                'best school': manager.list(),
                'rank': manager.list()
            }
            self.ncount = manager.Value('i', 1)
        else:
            self.res_dic = {
                'file name': [],
                'highest degree': [],
                'best school': [],
                'rank': []
            }
            self.ncount = 1
        self.result = None

        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', None)

    def get_rank_info(self, res_dict, count, total_file_num, file_name):
        '''
        Extract info from parser class. Get highest education and its ranking.
        '''
        start_time = time.time()
        output = ResumeParser(self.path + file_name).get_extracted_data()

        res_dict['file name'].append(file_name.split('.')[0])
        try:
            res_dict['highest degree'].append(output['degree'][0])
        except IndexError:
            res_dict['highest degree'].append('NaN')
        try:
            best_school = max(output['college_name'],
                              key=output['college_name'].get)
            res_dict['best school'].append(best_school)
            res_dict['rank'].append(output['college_name'][best_school])
        except KeyError:
            res_dict['best school'].append('NaN')
            res_dict['rank'].append(float('NaN'))

        print(f'file processed: {count.value}/{total_file_num}. \
            --- {(time.time() - start_time):.2f} seconds ---')
        count.value += 1

    # @timer
    def run(self):
        '''
        Main function to process the resumes ranking and sorting.
        '''

        total_file_num = len(listdir(self.path))
        print('\nStart calculating ranks...')
        print('Total time is not accurate for multiprocessing...\n')
        if self.multiproc:  # use multiprocessing
            func = partial(self.get_rank_info, self.res_dic,
                           self.ncount, total_file_num)

            with mp.Pool(mp.cpu_count()) as pool:
                pool.map(func, listdir(self.path))

            self.res_dic = {k: list(v) for k, v in self.res_dic.items()}

        else:  # don't use multiprocessing
            for file_name in listdir(self.path):
                self.get_rank_info(self.res_dic, self.ncount,
                                   total_file_num, file_name)

        self.result = pd.DataFrame(self.res_dic).sort_values(
            by=['rank'], ignore_index=True)

    def export_result(self, print_res=True, save=True, path='.'):
        '''
        Function to export results. Print in command line or save as csv.
        '''
        self.run()
        if print_res:
            print('\n', self.result)
        if save:
            self.result.to_csv(path+'/ranking.csv')


if __name__ == '__main__':
    mp.freeze_support()
    RankingModel = ResumeRank()
    RankingModel.export_result()

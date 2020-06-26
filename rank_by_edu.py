import sys
from os import listdir
# sys.path.append('../pyresparser')
from resparser import ResumeParser
import pandas as pd
import time


path = './resume/'
res_dic = {
'file name':[],
'highest degree':[],
'best school':[],
'rank':[]
}

total_file_num = len(listdir(path))
for i, file_name in enumerate(listdir(path)):
    start_time = time.time()

    output = ResumeParser(path+file_name).get_extracted_data()

    res_dic['file name'].append(file_name.split('.')[0])
    try:
        res_dic['highest degree'].append(output['degree'][0])
    except:
        res_dic['highest degree'].append('NaN')
    try:
        best_school = max(output['college_name'], key=output['college_name'].get)
        res_dic['best school'].append(best_school)
        res_dic['rank'].append(output['college_name'][best_school])
    except:
        res_dic['best school'].append('NaN')
        res_dic['rank'].append(float('NaN'))

    print('file processed: {}/{}. --- {:2f} seconds ---'.format(i+1, \
                    total_file_num, time.time() - start_time))


result = pd.DataFrame(res_dic)
result = result.sort_values(by=['rank'], ignore_index=True)

pd.set_option('display.max_columns', 10)
print(result)

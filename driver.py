'''
a sample program to do the resume extraction and ranking.
'''
from pprint import pprint
from resparser import ResumeParser, ResumeRank

def main():
    '''
    Main function.
    '''

    # extraction part
    data1 = ResumeParser('../resume/Resume_Jason(ZhixingHe).pdf').get_extracted_data()
    pprint(data1)

    # data2 = ResumeParser(
    #     'resume/Resume.Pyae Hein.pdf').get_extracted_data()
    # pprint(data2)

    # ranking part
    ranking_class = ResumeRank(res_path='./resume/', multiproc=True)
    ranking_class.export_result()

if __name__ == "__main__":
    main()

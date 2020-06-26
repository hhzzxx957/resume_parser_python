from pprint import pprint
from resparser import ResumeParser

data1 = ResumeParser('../resume/Resume_Jason(ZhixingHe).pdf').get_extracted_data()
pprint(data1)

# data2 = ResumeParser(
#     'resume/Resume.Pyae Hein.pdf').get_extracted_data()
# pprint(data2)

'''
Constant file.
'''
# from nltk.corpus import stopwords
import spacy
sp = spacy.load('en_core_web_sm')

# Omkar Pathak
NAME_PATTERN = [{'POS': 'PROPN'}, {'POS': 'PROPN'}]
# NAME_PATTERN2 = [{'POS': 'PROPN'}, {'POS': 'PROPN'}, {'POS':'PROPN'}]

# Education (Upper Case Mandatory)
EDUCATION = [
    'BE', 'B.E.', 'B.E', 'BS', 'B.S', 'B.S.', 'BACHELOR',
    'ME', 'M.E', 'MS', 'M.S', 'M.S.', 'BTECH', 'MTECH', 'MASTER',
    'PHD', 'PH.D', 'PH.D.', 'MD', 'M.D.', 'M.D', 'DOCTOR',
    'SSC', 'HSC', 'CBSE', 'ICSE', 'X', 'XII'
]

NOT_ALPHA_NUMERIC = r'[^a-zA-Z\d]'

NUMBER = r'\d+'

# For finding date ranges
MONTHS_SHORT = r'''(jan)|(feb)|(mar)|(apr)|(may)|(jun)|(jul)
                   |(aug)|(sep)|(oct)|(nov)|(dec)'''
MONTHS_LONG = r'''(january)|(february)|(march)|(april)|(may)|(june)|(july)|
                   (august)|(september)|(october)|(november)|(december)'''
MONTH = r'(' + MONTHS_SHORT + r'|' + MONTHS_LONG + r')'
YEAR = r'(((20|19)(\d{2})))'

# STOPWORDS = set(stopwords.words('english'))
STOPWORDS = sp.Defaults.stop_words

RESUME_SECTIONS_PROFESSIONAL = [
    'experience',
    'education',
    'interests',
    'professional experience',
    'publications',
    'skills',
    'certifications',
    'objective',
    'career objective',
    'summary',
    'leadership'
]

RESUME_SECTIONS_GRAD = [
    'accomplishments',
    'education',
    'employment',
    'experience',
    'interests',
    'projects',
    'profile',
    'publications',
    'skills',
    'certifications',
    'objective',
    'summary',
    'introduction'
]
SECTION_NAMELIST = {
    'profile': ['beginning', 'introduction', 'profile', 'summary'],
    'education': ['education', 'publications', 'certifications'],
    'skills': ['skills', 'projects', 'experience'],
    'experience': ['experience', 'projects', 'employment']
}

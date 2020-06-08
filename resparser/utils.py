# Author: Omkar Pathak

import io
import os
import re
import nltk
import pandas as pd
import docx2txt
from datetime import datetime
from dateutil import relativedelta
from . import constants as cs
from pdfminer.converter import TextConverter
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFSyntaxError
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords


def extract_text_from_pdf(pdf_path):
    '''
    Helper function to extract the plain text from .pdf files

    :param pdf_path: path to PDF file to be extracted (remote or local)
    :return: iterator of string of extracted text
    '''
    # https://www.blog.pythonlibrary.org/2018/05/03/exporting-data-from-pdfs-with-python/
    if not isinstance(pdf_path, io.BytesIO):
        # extract text from local pdf file
        with open(pdf_path, 'rb') as fh:
            try:
                for page in PDFPage.get_pages(
                        fh,
                        caching=True,
                        check_extractable=True
                ):
                    resource_manager = PDFResourceManager()
                    fake_file_handle = io.StringIO()
                    converter = TextConverter(
                        resource_manager,
                        fake_file_handle,
                        codec='utf-8',
                        laparams=LAParams()
                    )
                    page_interpreter = PDFPageInterpreter(
                        resource_manager,
                        converter
                    )
                    page_interpreter.process_page(page)

                    text = fake_file_handle.getvalue()
                    yield text

                    # close open handles
                    converter.close()
                    fake_file_handle.close()
            except PDFSyntaxError:
                return
    else:
        # extract text from remote pdf file
        try:
            for page in PDFPage.get_pages(
                    pdf_path,
                    caching=True,
                    check_extractable=True
            ):
                resource_manager = PDFResourceManager()
                fake_file_handle = io.StringIO()
                converter = TextConverter(
                    resource_manager,
                    fake_file_handle,
                    codec='utf-8',
                    laparams=LAParams()
                )
                page_interpreter = PDFPageInterpreter(
                    resource_manager,
                    converter
                )
                page_interpreter.process_page(page)

                text = fake_file_handle.getvalue()
                yield text

                # close open handles
                converter.close()
                fake_file_handle.close()
        except PDFSyntaxError:
            return


def get_number_of_pages(file_name):
    try:
        if isinstance(file_name, io.BytesIO):
            # for remote pdf file
            count = 0
            for page in PDFPage.get_pages(
                        file_name,
                        caching=True,
                        check_extractable=True
            ):
                count += 1
            return count
        else:
            # for local pdf file
            if file_name.endswith('.pdf'):
                count = 0
                with open(file_name, 'rb') as fh:
                    for page in PDFPage.get_pages(
                            fh,
                            caching=True,
                            check_extractable=True
                    ):
                        count += 1
                return count
            else:
                return None
    except PDFSyntaxError:
        return None


def extract_text_from_docx(doc_path):
    '''
    Helper function to extract plain text from .docx files

    :param doc_path: path to .docx file to be extracted
    :return: string of extracted text
    '''
    try:
        temp = docx2txt.process(doc_path)
        text = [line.replace('\t', ' ') for line in temp.split('\n') if line]
        return ' '.join(text)
    except KeyError:
        return ' '


def extract_text_from_doc(doc_path):
    '''
    Helper function to extract plain text from .doc files

    :param doc_path: path to .doc file to be extracted
    :return: string of extracted text
    '''
    try:
        try:
            import textract
        except ImportError:
            return ' '
        text = textract.process(doc_path).decode('utf-8')
        return text
    except KeyError:
        return ' '


def extract_text(file_path, extension):
    '''
    Wrapper function to detect the file extension and call text
    extraction function accordingly

    :param file_path: path of file of which text is to be extracted
    :param extension: extension of file `file_name`
    '''
    text = ''
    if extension == '.pdf':
        for page in extract_text_from_pdf(file_path):
            text += ' ' + page
    elif extension == '.docx':
        text = extract_text_from_docx(file_path)
    elif extension == '.doc':
        text = extract_text_from_doc(file_path)
    return text


def extract_entity_sections(text_raw):
    '''
    Helper function to extract all the raw text from sections of
    resume specifically for graduates and undergraduates

    :param text: Raw text of resume
    :return: dictionary of entities
    '''
    text_split = [i.strip() for i in text_raw.split('\n')]
    # sections_in_resume = [i for i in text_split if i.lower() in sections]
    sections = {'beginning': []}
    key = False
    for phrase in text_split:
        if len(phrase) == 1:
            p_key = phrase
        else:
            p_key = set(phrase.lower().split()) & set(cs.RESUME_SECTIONS_GRAD)
        try:
            p_key = list(p_key)[0]
        except IndexError:
            pass

        if not p_key and not key and phrase.strip():
            sections['beginning'].append(phrase)
        elif p_key in cs.RESUME_SECTIONS_GRAD:
            sections[p_key] = []
            key = p_key
        elif key and phrase.strip():
            sections[key].append(phrase)
    return sections

def extract_section_text(section_title, sections):
    '''
    helper function to extract text by from each section
    including profile, experience, skills, education
    '''
    section_list = cs.SECTION_NAMELIST[section_title]
    text_section = []
    for section_name in section_list:
        if section_name in sections.keys():
            text_section += sections[section_name]
    return '\n'.join(text_section)

def extract_entities_form_model(custom_nlp_text):
    '''
    Helper function to extract different entities with custom
    trained model using SpaCy's NER

    :param custom_nlp_text: object of `spacy.tokens.doc.Doc`
    :return: dictionary of entities
    '''
    entities = {}
    for ent in custom_nlp_text.ents:
        if ent.label_ not in entities.keys():
            entities[ent.label_] = [ent.text]
        else:
            entities[ent.label_].append(ent.text)
    for key in entities.keys():
        entities[key] = list(set(entities[key]))
    return entities

def get_total_experience(experience_text):
    '''
    Wrapper function to extract total months of experience from a resume

    :param experience_phrases: list of experience phrase extracted
    :return: total months of experience
    '''
    experience_phrases = experience_text.split('\n')
    experience_dic = {}
    exp_ = []
    for ind, line in enumerate(experience_phrases):
        experience = re.search(
            r'(?P<fmonth>\w+\.*.\d+)\s*(\D|to)\s*(?P<smonth>\w+\.*.\d+|present|current)',
            line,
            re.I
        )
        if experience:
            date = ' '.join(experience.groups(0))
            exp_.append(experience.groups(0))
            # add exprience to experience_list
            experience_dic[date] = []
            if line != date:
                experience_dic[date].append(line.replace(date, ''))
            try:
                experience_dic[date].append(experience_phrases[ind-1])
            except: pass
            try:
                experience_dic[date].append(experience_phrases[ind+1])
            except: pass

    total_exp = sum(
        [get_number_of_months_from_dates(i[0], i[2]) for i in exp_]
    )
    total_experience_in_months = total_exp
    return [total_experience_in_months, experience_dic]

def get_number_of_months_from_dates(date1, date2):
    '''
    Helper function to extract total months of experience from a resume

    :param date1: Starting date
    :param date2: Ending date
    :return: months of experience from date1 to date2
    '''
    if date2.lower() == 'present':
        date2 = datetime.now().strftime('%b %Y')
    try:
        if len(date1.split()[0]) > 3:
            date1 = date1.split()
            date1 = date1[0][:3] + ' ' + date1[1]
        if len(date2.split()[0]) > 3:
            date2 = date2.split()
            date2 = date2[0][:3] + ' ' + date2[1]
    except IndexError:
        return 0
    try:
        date1 = datetime.strptime(str(date1), '%b %Y')
        date2 = datetime.strptime(str(date2), '%b %Y')
        months_of_experience = relativedelta.relativedelta(date2, date1)
        months_of_experience = (months_of_experience.years
                                * 12 + months_of_experience.months)
    except ValueError:
        return 0
    return months_of_experience

def extract_email(text):
    '''
    Helper function to extract email id from text

    :param text: plain text extracted from resume file
    '''
    email = re.findall(r"([^@|\s]+@[^@]+\.[^@|\s]+)", text)
    if email:
        try:
            return email[0].split()[0].strip(';')
        except IndexError:
            return None

def preprocess(nlp_text, nlp):
    text = [w.text for w in nlp_text if not w.is_stop and not w.is_punct]
    return nlp(' '.join(text))

def extract_name(nlp_text, matcher):
    '''
    Helper function to extract name from spacy nlp text

    :param nlp_text: object of `spacy.tokens.doc.Doc`
    :param matcher: object of `spacy.matcher.Matcher`
    :return: string of full name
    '''
    # text = [w.text for w in nlp_text if not w.is_stop and w.pos_ != 'PUNCT']

    pattern = [cs.NAME_PATTERN]

    matcher.add('NAME', None, *pattern)

    matches = matcher(nlp_text)
    # print([(x.orth_, x.pos_,)
    #    for x in [y for y in nlp_text if not y.is_stop and y.pos_ != 'PUNCT']])

    first_sent = ''

    for _, start, end in matches:
        span = nlp_text[start:end]
        if 'name' not in span.text.lower():
            first_sent = span.text
            break

    fullname = []

    name_ent = [ee for ee in nlp_text.ents if ee.label_ == 'PERSON']

    # if name_ent in first matched pattern not in name_ent, add name_ent.
    if name_ent:
        fullname.append(name_ent[0])
        if str(name_ent[0]) not in str(first_sent):
            fullname.append(first_sent)
    else:
        fullname.append(first_sent)
    return fullname

def extract_company_name(nlp_text):
    college_df = pd.read_csv(
        os.path.join(os.path.dirname(__file__), 'world-universities.csv')
    )
    colleges = [college.upper() for college in list(college_df.name)]

    skills_df = pd.read_csv(
        os.path.join(os.path.dirname(__file__), 'skills.csv')
    )
    skills = [skill.upper() for skill in list(skills_df.columns.values)]

    companies = []
    for ee in nlp_text.ents:
        if ee.label_ == 'ORG' and str(ee).upper() not in colleges + skills:
            companies.append(ee)
    return companies

def extract_mobile_number(text, custom_regex=None):
    '''
    Helper function to extract mobile number from text

    :param text: plain text extracted from resume file
    :return: string of extracted mobile numbers
    '''
    if not custom_regex:
        mob_num_regex = ".*?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).*?"
#         mob_num_regex = r'''(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)
#                         [-\.\s]*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4})'''
        phone = re.findall(re.compile(mob_num_regex), text)
    else:
        phone = re.findall(re.compile(custom_regex), text)
    if phone:
        number = ''.join(phone[0])
        return number

def extract_skills(nlp_text, noun_chunks, skills_file=None):
    '''
    Helper function to extract skills from spacy nlp text

    :param nlp_text: object of `spacy.tokens.doc.Doc`
    :param noun_chunks: noun chunks extracted from nlp text
    :return: list of skills extracted
    '''
    tokens = [token.text for token in nlp_text if not token.is_stop]
    if not skills_file:
        data = pd.read_csv(
            os.path.join(os.path.dirname(__file__), 'skills.csv')
        )
    else:
        data = pd.read_csv(skills_file)
    skills = list(data.columns.values)
    skillset = []
    # check for one-grams
    for token in tokens:
        if token.lower() in skills:
            skillset.append(token)

    # check for bi-grams and tri-grams
    for token in noun_chunks:
        token = token.text.lower().strip()
        if token in skills:
            skillset.append(token)
    return [i.capitalize() for i in set([i.lower() for i in skillset])]

def cleanup(token, lower=True):
    if lower:
        token = token.lower()
    return token.strip()

def extract_designation(nlp_text, noun_chunks):
    title_df = pd.read_csv(
        os.path.join(os.path.dirname(__file__), 'jobtitles.csv')
    )

    titles = list(title_df.Title.values)
    titles = [title.lower() for title in titles]
    tokens = [token.text for token in nlp_text if not token.is_stop]

    titleset = []
    # check for one-grams
    for token in tokens:
        if token.lower() in titles:
            titleset.append(token)

    # check for bi-grams and tri-grams
    for token in noun_chunks:
        token = token.text.lower().strip()
        if token in titles:
            titleset.append(token)
    return [i.capitalize() for i in set([i.lower() for i in titleset])]

def extract_degree(nlp_text_sents):
    '''
    Helper function to extract education from spacy nlp text

    :param nlp_text: object of `spacy.tokens.doc.Doc`
    :return: tuple of education degree and year if year if found
             else only returns education degree
    '''
    # Extract education degree
    edu = {}
    try:
        for index, text in enumerate(nlp_text_sents):
            for tex in text.split():
                tex = re.sub(r'[?|$|.|!|,]', r'', tex)
                if tex.upper() in cs.EDUCATION and tex not in cs.STOPWORDS:
                    edu[tex] = text + nlp_text_sents[index + 1]
    except IndexError:
        pass

    # Extract major & year
    majors_df = pd.read_csv(
        os.path.join(os.path.dirname(__file__), 'majorslist.csv')
    )
    majors = list(majors_df.Major)

    education =[]
    for key in edu.keys():
        major = [major for major in majors if major in edu[key].upper()]
        year = re.search(re.compile(cs.YEAR), edu[key])

        edu_info = [key]
        if major:
            edu_info.append(major[0])
        if year:
            edu_info.append(''.join(year.group(0)))
        education.append(' '.join(edu_info))
    return education

def extract_college_name(nlp_text_sents):
    data = pd.read_csv(
            os.path.join(os.path.dirname(__file__), 'world-universities.csv')
            )

    colleges = list(data.name)
    collegeset = []
    for sent in nlp_text_sents:
        collegeset += [college for college in colleges if college.upper() in sent.upper()]
    return [i.capitalize() for i in set([i.lower() for i in collegeset])]

def extract_experience(resume_text):
    '''
    Helper function to extract experience from resume text

    :param resume_text: Plain resume text
    :return: list of experience
    '''
    wordnet_lemmatizer = WordNetLemmatizer()
    stop_words = set(stopwords.words('english'))

    # word tokenization
    word_tokens = nltk.word_tokenize(resume_text)

    # remove stop words and lemmatize
    filtered_sentence = [
            w for w in word_tokens if w not
            in stop_words and wordnet_lemmatizer.lemmatize(w)
            not in stop_words
        ]
    sent = nltk.pos_tag(filtered_sentence)
    print('sent',sent)
    # parse regex
    cp = nltk.RegexpParser('P: {<NNP>+}')
    cs = cp.parse(sent)
    print('cs',cs)
    # for i in cs.subtrees(filter=lambda x: x.label() == 'P'):
    #     print(i)

    test = []

    for vp in list(
        cs.subtrees(filter=lambda x: x.label() == 'P')
    ):
        test.append(" ".join([
            i[0] for i in vp.leaves()
            if len(vp.leaves()) >= 2])
        )
    print('test',test)
    # Search the word 'experience' in the chunk and
    # then print out the text after it
    x = [
        x[x.lower().index('experience') + 10:]
        for i, x in enumerate(test)
        if x and 'experience' in x.lower()
    ]
    return x

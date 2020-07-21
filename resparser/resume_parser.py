# -*- coding: utf-8 -*-
'''
Main program for ResumeParser.
'''
import os
import multiprocessing as mp
import io
import pprint
import spacy
from spacy.matcher import Matcher
from . import utils

class ResumeParser(object):
    '''Main class'''

    def __init__(
            self,
            resume,
            skills_file=None,
            custom_regex=None
    ):
        nlp = spacy.load('en_core_web_sm')
        custom_nlp = spacy.load(os.path.dirname(
            os.path.abspath(__file__)) + '/model')

        self.__skills_file = skills_file
        self.__custom_regex = custom_regex
        self.__matcher = Matcher(nlp.vocab)
        self.__details = {
            'name': None,
            'email': None,
            'mobile_number': None,
            'skills': None,
            'college_name': None,
            'degree': None,
            'designation': None,
            'experience': None,
            'company_names': None,
            'no_of_pages': None,
            'total_experience': None,
        }
        self.__resume = resume
        if not isinstance(self.__resume, io.BytesIO):
            ext = os.path.splitext(self.__resume)[1].split('.')[1]
        else:
            ext = self.__resume.name.split('.')[1]
        self.__text_raw = utils.extract_text(self.__resume, '.' + ext)
        self.__text = ' '.join(self.__text_raw.split())
        self.__nlp = nlp(self.__text)
        self.__noun_chunks = list(self.__nlp.noun_chunks)
        self.__nlp_sents = [sent.string.strip() for sent in self.__nlp.sents]
        self.__custom_nlp = custom_nlp(self.__text_raw)
        self.__cust_ent = utils.extract_entities_form_model(self.__custom_nlp)
        # info split by sections
        # profile section
        self.__sections = utils.extract_entity_sections(self.__text_raw)
        self.__text_profile = utils.extract_section_text(
            'profile', self.__sections)
        self.__nlp_profile = nlp(self.__text_profile)
        self.__nlp_profile = utils.preprocess(self.__nlp_profile, nlp)
        # education section
        self.__text_edu = utils.extract_section_text(
            'education', self.__sections)
        self.__nlp_edu = nlp(self.__text_edu)
        self.__nlp_sents_edu = [sent.string.strip()
                                for sent in self.__nlp_edu.sents]
        # experience section
        self.__text_experience = utils.extract_section_text(
            'experience', self.__sections)
        self.__nlp_experience = nlp(self.__text_experience)
        [self.__exp_date, self.__exp_dic] = utils.get_total_experience(
            self.__text_experience)
        try:
            self.__nlp_exp_dic = nlp(
                ' '.join(list(self.__exp_dic.values())[0]))
        except IndexError:
            self.__nlp_exp_dic = nlp('')

        self.__get_basic_details()


    def get_extracted_data(self):
        '''
        Output extraction.
        '''
        return self.__details

    # @utils.timer
    def __get_basic_details(self):
        '''
        Get profile info.
        '''
        name = utils.extract_name(self.__nlp_profile, matcher=self.__matcher)
        if not name:
            name = utils.extract_name(self.__nlp, matcher=self.__matcher)

        email = utils.extract_email(self.__text)
        mobile = utils.extract_mobile_number(self.__text, self.__custom_regex)
        # get education info
        degree = utils.extract_degree(self.__nlp_sents_edu)
        if not degree:
            degree = utils.extract_degree(self.__nlp_sents)

        college_name = utils.extract_college_name(self.__nlp_sents_edu)
        if not college_name:
            college_name = utils.extract_college_name(self.__nlp_sents)

        # get work experience info
        designation = utils.extract_designation(self.__nlp, self.__noun_chunks)

        company_names = utils.extract_company_name(self.__nlp_exp_dic)
        if not company_names:
            company_names = utils.extract_company_name(self.__nlp_experience)
        if not company_names:
            company_names = utils.extract_company_name(self.__nlp)

        # get skill info
        skills = utils.extract_skills(
            self.__nlp,
            self.__noun_chunks,
            self.__skills_file
        )

        # extract name
        try:
            self.__details['name'] = self.__cust_ent['Name'][0]
        except (IndexError, KeyError):
            self.__details['name'] = name

        # extract email
        self.__details['email'] = email

        # extract mobile number
        self.__details['mobile_number'] = mobile

        # extract skills
        self.__details['skills'] = skills

        # extract college name
        self.__details['college_name'] = college_name

        # extract education Degree
        self.__details['degree'] = degree

        # extract experience
        self.__details['experience'] = self.__exp_dic
        try:
            exp = round(self.__exp_date / 12, 2)
            self.__details['total_experience'] = exp
        except KeyError:
            self.__details['total_experience'] = 0

        # extract designation
        self.__details['designation'] = designation
        try:
            self.__details['designation'].extend(
                self.__cust_ent['Designation'])
        except KeyError:
            pass

        self.__details['company_names'] = company_names

        self.__details['no_of_pages'] = utils.get_number_of_pages(
            self.__resume
        )
        return


def resume_result_wrapper(resume):
    '''
    Wrapper for multiprocessing
    '''
    parser = ResumeParser(resume)
    return parser.get_extracted_data()


if __name__ == '__main__':
    pool = mp.Pool(mp.cpu_count())

    resumes = []
    data = []
    for root, directories, filenames in os.walk('resumes/'):
        for filename in filenames:
            file = os.path.join(root, filename)
            resumes.append(file)

    results = [
        pool.apply_async(
            resume_result_wrapper,
            args=(x,)
        ) for x in resumes
    ]

    results = [p.get() for p in results]

    pprint.pprint(results)

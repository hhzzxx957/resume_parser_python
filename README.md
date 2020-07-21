# Resume parser in Python
Extract information from resumes/CVs, including name, college, degree, phone, skills, experience, company name, designation.

Support PDF and DOCx files.

Keep updating.

# How to use
Install dependencies from resparser/requirements.txt

Install neccesary spacy model.
```bash
# spaCy
python -m spacy download en_core_web_sm
```

Run default driver.py to see example output.

Add your target resume in resume folder and change file address in driver.py. 

Run driver.py in command line.
```bash
python driver.py
```

Done! Result will be printed.

Here is an example result:

```
{'college_name': {'Virginia Tech': 157, 'Zhejiang University': 84},
 'company_names': [Python NLTK, Kaggle, Python Flask, AWS EMR],
 'degree': ['PhD PHYSICS 2013', 'BS PHYSICS 2013'],
 'designation': ['Testing', 'Model'],
 'email': 'he***@gmail.com',
 'experience': {'Aug 2009 - May 2013': ['Aug 2013 - Mar 2020',
                                        'Nano-structure detection by '
                                        'quantitative optical anisotropy '
                                        'imaging'],
                'Aug 2013 - Mar 2020': ['B.S. in Physics',
                                        'Aug 2009 - May 2013'],
                'Jan 2018 - Jun 2019': ['Toxic Comment Classification and '
                                        'Analysis',
                                        '• Identified and classified half '
                                        'million toxic Wikipedia comments by '
                                        'Bidirectional LSTM neural network'],
                                        ...
                                        },
 'mobile_number': '(703) 625-****',
 'name': [Zhixing Jason],
 'no_of_pages': 1,
 'skills': ['Math',
            'R',
            'Matplotlib',
            'Github',
            'Time management',
            ...
            ],
 'total_experience': 14.42}
 ```
# Try here
Upload your pdf/docx resume on [here](https://jasonhe.pythonanywhere.com) to view the result.

# Ranking by education
User can rank multiple resume by education in resume folder. Multiprocessing is enabled when ranking multiple files.

Rank is based on the ranking of the best universities of the world made by [The Times Higher Education for 2020](https://www.timeshighereducation.com/world-university-rankings/2020/world-ranking#!/page/0/length/-1/sort_by/rank/sort_order/asc/cols/scores).

Here is an example output:
```
Start calculating ranks...
Total time is not accurate for multiprocessing...

file processed: 1/4.             --- 2.965085 seconds ---
file processed: 2/4.             --- 3.158208 seconds ---
file processed: 3/4.             --- 3.613191 seconds ---
file processed: 4/4.             --- 3.967168 seconds ---

                             file name                  highest degree                               best school  rank
0        jerome_rufin_resume_04_29_20                         BS 2016        University of California, Berkeley    13
1             Resume_Jason(ZhixingHe)                PhD PHYSICS 2013                             Virginia Tech   157
2  Alex_Suvorov_-_Full_Stack_Engineer  Bachelor COMPUTER SCIENCE 2015                      University of Warsaw   343
3                   Kormulev_short_CV                             NaN  Bauman Moscow State Technical University   410
```

# Customize
You can customize the parser easily by replacing your own skill, majorslist, world-universities csv in resparser folder.

You can also train your own spacy model (with your own labeled training data from other sources) by using the custom_train.py in model folder. The trained model can replaced the default model in resparser/model/

# Reference
This project is modified and improved from [Omkar Pathak's pyresparser](https://github.com/OmkarPathak/pyresparser).

Summaried code concepts from Priya, [here](https://medium.com/@divalicious.priya/information-extraction-from-cv-acec216c3f48).

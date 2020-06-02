# Resume parser in Python
Extract information from resumes/CVs, including name, college, degree, phone, skills, experience, company name, designation.

Support PDF and DOCx files.

Modified from Omkar Pathak's pyresparser, https://github.com/OmkarPathak/pyresparser. Keep updating.

# How to use?
Install dependencies from resparser/requirements.txt

Install neccesary spacy model and nltk words
```bash
# spaCy
python -m spacy download en_core_web_sm

# nltk
python -m nltk.downloader words
```

Add your target resume in resume folder and change file address in driver.py. 

Run driver.py in command line.
```bash
python driver.py
```

Done! Result will be printed.

Here is the example result:

```
{'college_name': ['Zhejiang University', 'Virginia Tech'],
 'company_names': None,
 'degree': ['PhD PHYSICS 2013', 'BS PHYSICS 2013'],
 'designation': None,
 'email': 'hezhixing957@gmail.com',
 'experience': ['Nano-structure detection by quantitative optical anisotropy '
                'imaging',
                'Oct 2017 - Dec 2019',
                '• Designed a novel optical system with fast acquisition and '
                'high precision by combining the classical optical detection',
                'with fast Fourier transform (FFT)-based digital signal '
                ...
 'mobile_number': '(703) 625-****',
 'name': Jason,
 'no_of_pages': 1,
 'skills': ['Communication',
            'Statistics',
            'Sql',
            'Acquisition',
            'Physics',
            ...
 'total_experience': 4.08}
 ```
# Customize
You can customize the parser easily by replacing your own skill, majorslist, world-universities csv in resparser folder.

You can also train your own spacy model (with your own labeled training data from other sources) by using the custom_train.py in model folder. The trained model can replaced the default model in resparser/model/

# Reference
Great thanks to Omkar Pathak's pyresparser, https://github.com/OmkarPathak/pyresparser

Summaried code concepts from Priya, https://medium.com/@divalicious.priya/information-extraction-from-cv-acec216c3f48.

import pandas as pd
import numpy as np
import re


def extract_title_info(txt):
    '''
    Extract information from title string
    
    Args:
        txt: a text that contains course title information
        
    Returns:
        The title, the course full name, and number of unit
        
        Example output: ('DSC 10', 'Principles of Data Science', '(4)')
    '''

    title = re.findall(r'(\(?[A-Z]{2,}\)? [0-9/]+[A-Z\-]{0,})\.?', txt)[0]
    txt = txt.replace(title, '')

    # case when unit is not specified 
    if txt.find('(') == -1:
        name = re.findall(r'\.? ([\w\W]+)', txt)[0]
        unit = 'N/A'
    else: 
        name = re.findall(r'\.? ([\w\W]+) \(', txt)[0]
        txt = txt.replace(name, '')

        # searching for special character
        unit = re.findall('\([\./\w,\s–-]+\)', txt)[0]
    
    return title, name, unit


def extract_preq(txt):
    '''
    Extract information from description string
    
    Args:
        txt: a text that contains course description information
        
    Returns:
        The course description and the course prerequisties
        
        Example output: ('Economic issues ... coral reefs.', 'Prerequisites: ECON 2 or 100A.')
    '''
    
    # checking if the given string is nan
    if txt != txt:
        prereq = 'N/A'
    else:
        # fix encoding error
        txt = txt.replace(u'\xa0', u' ')

        if re.search('Prerequisites:', txt):
            prereq = re.search(r'Prerequisites: (none|[^\.;]+|)(\.?|;?)', txt).group(0)
            txt = txt.replace(prereq, '')
        else:
            prereq = 'N/A'
    
    return txt, prereq


def extract_preq_courses(txt):
    '''
    Extract course prerequisties info from prerequisties string
    
    Args:
        txt: a text that contains course prerequisties information
        
    Returns:
        The course prerequisties and whether the course has strict course prerequisite
        
        The course prerequisties is a list of list, 
        the outer list represents each of the prerequisite, 
        the inner list represents the equivalent courses for satisfying a prerequisite, 
        
        Example output: 
            ('[[MATH 10A, MATH 20A], [MATH 10B, MATH 20B], [DSC 40A]]', 'True')
            ('upper-division standing.', 'False')
    '''
    
    course_prereq = []
    has_course_prereq = True

    for equivalent_courses in list(filter(None, re.split(', (?!(or))|and', txt.strip()))):

        equ_course = []

        if equivalent_courses.strip():

            for course in re.split('or', equivalent_courses):
                if ('consent' not in course and re.search(r'[A-Z]{2,} [0-9]{1,3}', course)):
                    # extract course keyword pattern
                    course = re.findall(r'[A-Z]{2,} [0-9]{1,3}[A-Z\-]{0,}', course)[0]
                    equ_course.append(course.strip('() '))

            # remove empty elements
            equ_course = list(filter(None, equ_course))

        if len(equ_course) != 0:
            course_prereq.append(equ_course)

    if len(course_prereq) == 0:
        course_prereq = txt.replace('Prerequisites: ', '')
        has_course_prereq = False
    
    return course_prereq, has_course_prereq


if __name__ == '__main__':
    raw_data = pd.read_csv('data/raw_data.csv', header=None, names=['course_title', 'course_description'])

    # extract title information
    title_df = pd.DataFrame(raw_data['course_title'].apply(extract_title_info).to_list(), 
                            columns=['title', 'name', 'unit'])

    department_df = title_df['title'].str.split().str[0]
    department_df.name = 'department'

    title_df = pd.concat([title_df, department_df], axis=1)

    # extract description information
    desc_df = pd.DataFrame(raw_data['course_description'].apply(extract_preq).to_list(), 
                        columns=['description', 'prereq'])

    prereq_df = pd.DataFrame(desc_df['prereq'].apply(extract_preq_courses).to_list(), 
                            columns=['prereq', 'has_prereq'])

    desc_df = pd.concat([desc_df['description'], prereq_df], axis=1)

    # concatenate both dataframe
    df = pd.concat([title_df, desc_df], axis=1)

    # write to csv file
    df.to_csv('data/course_data.csv', index=False)



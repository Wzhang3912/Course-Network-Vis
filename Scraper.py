import requests
from bs4 import BeautifulSoup
import csv


def scrape():
    '''
    Scrape courses information and store it in csv, where the first column is the course title 
    and the second column is the course description
    '''

    main_page_url = 'https://catalog.ucsd.edu/front/courses.html'
    header_url = 'https://catalog.ucsd.edu/'
    
    request = requests.get(main_page_url)
    soup = BeautifulSoup(request.text, 'lxml')

    csv_path = 'course_data.csv'

    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)

        for link in soup.findAll('a', string='courses'):
            catalog_url = header_url + link['href'][3:]
            
            # request for courses in each department
            request = requests.get(catalog_url, timeout=5)
            course = BeautifulSoup(request.text, 'lxml')

            for name_tag in course.findAll("p", "course-name"):
                course_name = name_tag.text.strip()
                course_name = " ".join(course_name.split())

                course_desc = name_tag.find_next('p').text

                writer.writerow([course_name, course_desc])
                
if __name__ == '__main__':
    scrape()



"""
university_data.py - ALL hardcoded data for SAUK119 system
"""

# ============= EXISTING (KEEP) =============
PAKISTANI_UNIVERSITIES = [
    'NUST', 'FUAST', 'Foundation University', 'Habib University', 'Hajvery University', 'LUMS', 'PIEAS', 'COMSATS', 'BZU', 'University of Punjab',
    'Quaid-i-Azam University', 'Iqra', 'Bahria', 'IBA Karachi', 'Jinnah University for Women', 'Mirpur University of Science and Tech', 'UMT',
    'AIR', 'FC College', 'University of South Asia', 'National Textile UF', 'NFC Institute of Engineering and Tech', 'Riphah International',
    'University of Lahore', 'University of Gujrat', 'Qurtaba University of Science and IT', 'Sarhad University of Science and IT', 'NUML',
    'University of Sargodha', 'University of Azad Jammu and Kashmir', 'University of Education', 'University of Kotli Azad Kashmir',
    'University of Poonch Azad Kashmir', 'Fatima Jinnah Women University Rawalpindi', 'Muhammad Nawaz Sharif University of Agriculture', 
    'Beaconhouse National University', 'National Defense University', 'Pakistan Institute of Development Economics', 'University of Health Sciences Lahore',
    'Ghulam Ishaq Khan GIKI', 'Fast NUCES', 'National College of Business NCBAE', 'University of Malakand', 'Mehran University of Engineering and Tech',
    'GIFT University', 'National College of Arts', 'Government College Lahore GCUF', 'Government College University Lahore', 'Government College Lahore',
    'Hamdard University Karachi', 'Lahore School of Economics LSE', 'Greenwhich University Karachi', 'Indus Valley School of Arts and Architecture',
    'Aitchison College Lahore ACL', 'Nadirshaw Edulji Dinshaw NED', 'University College Lahore', 'Lahore Grammar University', 'Hazara University',
    'Liaqat University LUMHS', 'Muhammad Ali Jinnah MAJU', 'Arid Agriculture PMAS', 'Khyber Medical University', 'University College of Medicine and Dentistry',
    'University of Agriculture Faisalabad', 'University of Engineering and Technology',
    'Islamia University Bahawalpur', 'Quaid e Azam University Islamabad', 'University of Sahiwal',
    'Shaheed Zulfiqar Ali SZABIST', 'Karachi Institute of Economics KIET',
    'Lahore Garrison University', 'Institute of Management Sciences Peshawar',
    'Institute of Space and Technology ISB', 'Institute of Fashion and Design',
    'Institute of Business Administration Sukkur', 'Institute of Business Management Karachi',
    'International Islamic University ISB', 'Aga Khan University Karachi',
    'Kinnaird College for Women LHR', 'Lahore College for Women University',
    'Superior University Lahore', 'University of Faisalabad TUF',
    'University of Balochistan Quetta', 'University of Central Punjab',
    'Zia ud Din University Karachi', 'University of Haripur',
    'University of Veterinary UVAS LHR', 'Roots Ivy International College',
    'Universal College Lahore', 'University of Peshawar', 'Balochistan University BUITEMS',
    'City University of Science and IT', 'CESCO University of IT and ES',
    'Qarshi University', 'Salim Habib University', 'UET Taxila',
    'King Edward Medical University', 'Baqai Medical University',
    'Allama Iqbal Medical College', 'University College of Medicine and DC',
    'Lahore Medical and Dental College', 'Islam Medical College', 'Ameer ud Din Medical College',
    'Islamabad Medical and Dental College', 'Nawaz Sharif Medical College',
    'Shalamar Medical and Dental College', 'FMH College of Medicince and Dentistry',
    'Avicenna Medical College', 'Multan Medical and Dental College',
    'Islamic International Dental C and H', 'Rashid Latif Medical College',
    'Sheikh Khalifa Bin Zayed', 'Al Nahyan Medical and Dental College',
    'Bacha Khan Medical College', 'Jinnah Medical and Dental College',
    'United Medical and Dental College', 'Pak Red Crescent Medical and DC',
    'Dadabhoy Institute of Higher Education', 'Dawood University of Engineering and Technology',
    'NED University of Engineering and Technology', 'Sir Syed University of Enginnering and Tech',
    'University of Karachi', 'University of Sialkot', 'UET Peshawar', 'GCUF', 'Abasyn', 
    'Capital University of Science and Tech', 'Dow University DUHS', 'National University of Computer and Emerging Sciences', 'IQRA National'
]

FIELD_NAMES = [
    'Business & Management',
    'IT & Computer Science',
    'Engineering & Technology',
    'Medical & Health Sciences',
    'Arts & Humanities',
    'Science & Natural Sciences',
    'Law & Legal Studies',
    'Education & Teaching',
    'Social Sciences',
    'Media & Communication',
    'Architecture & Design',
    'Agriculture & Forestry',
    'Hospitality & Tourism',
    'Aviation & Aeronautics',
    'Pharmacy',
    'Dentistry',
    'Nursing',
    'Psychology',
    'Environmental Sciences',
    'Mathematics & Statistics',
    'Physics',
    'Chemistry',
    'Biology',
    'Economics',
    'Finance & Accounting',
    'Political Science & International Relations',
    'Criminology & Forensic Science',
    'Public Health',
    'Biomedical Sciences',
    'Computer Engineering',
    'Artificial Intelligence & Data Science',
    'Cyber Security',
    'Mechanical Engineering',
    'Civil Engineering',
    'Electrical & Electronic Engineering',
    'Chemical Engineering',
    'Aerospace Engineering',
    'Automotive Engineering',
    'Robotics & Mechatronics',
    'Geology & Earth Sciences',
    'Environmental Engineering',
    'Biotechnology',
    'Food Science & Nutrition',
    'Sports Science',
    'Supply Chain & Logistics',
    'Marketing & Advertising',
    'Human Resource Management',
    'International Business',
    'Project Management',
    'Business Analytics',
    'Digital Marketing',
    'Accounting',
    'Finance',
    'Econometrics',
    'International Economics',
    'Software Engineering',
    'Information Systems',
    'Data Science',
    'Computer Networks',
    'Cloud Computing',
    'Web Development',
    'Game Development',
    'Animation & VFX',
    'Graphic Design',
    'Interior Design',
    'Fashion Design',
    'Fashion Management',
    'Performing Arts',
    'Music Production',
    'Film & Television Production',
    'Creative Writing',
    'English Literature',
    'History',
    'Philosophy',
    'Sociology',
    'Anthropology',
    'Public Administration',
    'Human Geography',
    'Urban Planning',
    'Construction Management',
    'Quantity Surveying',
    'Real Estate Management',
    'Renewable Energy Engineering',
    'Marine Biology',
    'Microbiology',
    'Molecular Biology',
    'Genetics',
    'Statistics & Data Analytics',
    'Health & Social Care',
    'Occupational Therapy',
    'Physiotherapy',
    'Radiography',
    'Optometry',
    'Veterinary Science',
    'Nutrition & Dietetics',
    'Speech & Language Therapy',
    'Tourism Management',
    'Event Management',
    'Logistics Management',
    'Entrepreneurship',
    'Leadership & Management'
]

ENGLISH_TESTS = {
    'ielts_ukvi': {'name': 'IELTS UKVI', 'scores': [4.0, 4.5, 5.0, 5.5, 6.0, 6.5, 7.0, 7.5, 8.0, 8.5]},
    'pte_ukvi': {'name': 'PTE UKVI', 'scores': list(range(40, 87))},
    'oxford_ellt': {'name': 'Oxford ELLT', 'scores': [4, 5, 6, 7, 8, 9]},
    'esol': {'name': 'ESOL', 'scores': list(range(20, 47))},
    'toefl': {'name': 'TOEFL', 'scores': list(range(51, 106))},
    'duolingo': {'name': 'Duolingo', 'scores': list(range(60, 141))},
    'ielts_academic': {'name': 'IELTS Academic', 'scores': [4.0, 4.5, 5.0, 5.5, 6.0, 6.5, 7.0, 7.5, 8.0, 8.5]},
    'pte_academic': {'name': 'PTE Academic', 'scores': list(range(40, 87))},
}

# ============= NEW ADDITIONS =============

COUNTRIES = [
    'United Kingdom',
    'United States', 
    'Canada',
    'Australia',
    'Hungary',
    'France',
    'Germany'
]

COUNTRY_LOCATIONS = {
    'United Kingdom': ['London', 'Manchester', 'Birmingham', 'Liverpool', 'Leeds', 'Glasgow', 'Southwales', 'Canterbury', 'Bedford', 'Bristol',
                       'Edinburgh', 'Sheffield', 'Leicester', 'Bangor', 'Wolverhampton', 'Sunderland', 'Durham', 'Hull', 'Salford', 'Lancaster', 'Coventry',
                       'Bradford', 'Newcastle', 'Nottingham', 'Chester', 'Warrington', 'Portsmouth', 'Southampton', 'Winchester', 'Bournemouth', 'Bath',
                       'Cardiff', 'Wrexham', 'Dundee', 'Aberdeen', 'Stirling', 'Paisley', 'Gloucester', 'Derby'],
    'United States': ['New York', 'California', 'Texas', 'Florida', 'Chicago'],
    'Canada': ['Toronto', 'Vancouver', 'Montreal', 'Calgary', 'Ottawa'],
    'Australia': ['Sydney', 'Melbourne', 'Brisbane', 'Perth', 'Adelaide'],
    'Hungary': ['Budhapest', 'Debrecen', 'Szeged', 'Miskolc', 'Eger'],
    'France': ['Paris', 'Nancy', 'Lyon', 'Nice', 'Brest'],
    'Germany': ['Berlin', 'Munich', 'Frankfurt', 'Hamburg', 'Cologne']
}

STUDY_GAPS = ['No Gap'] + [f"{i} Year{'s' if i != 1 else ''}" for i in range(0, 21)]

CGPA_RANGES = [f"{i/10:.1f}" for i in range(18, 41)]

PERCENTAGE_RANGES = [f"{i}%" for i in range(40, 91)]

INTAKES = [f"{month} 2026" for month in [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
]]

DURATIONS = [f"{i} Year{'s' if i != 1 else ''}" for i in range(1, 6)]

FSC_CUTOFFS = ['No Direct Admission'] + [f"{i}%" for i in range(50, 91)]

MIN_FSC_WITH_BA = [f"{i}%" for i in range(50, 91)]

MIN_BA_MARKS = [f"{i}%" for i in range(45, 91)]

MOI_MIN_CGPA = [f"{i/10:.1f}" for i in range(18, 41)]

MOI_MIN_PERCENTAGE = [f"{i}%" for i in range(40, 91)]

MOI_MIN_FSC = [f"{i}%" for i in range(40, 91)]

STAFF_PERCENTAGES = list(range(40, 91))

STAFF_CGPA_VALUES = [i/10 for i in range(18, 41)]
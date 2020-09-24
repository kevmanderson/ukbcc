import pytest
import pandas as pd
from io import StringIO
import re
#import sqlite
#import textwrap

@pytest.fixture(scope='module')
def main_csv(tmpdir_factory):
    test_main_dat = (
    '"eid","21017-0.0","41270-0.1","6070-0.0","6119-0.0","6148-0.1","6148-0.2","53-0.0","4286-0.0","20137-0.0","21003-0.0","22182-0.0"\n'
'"1037918","21017_0_0","E119","2","","4","5","1/10/2008","","2014-12-09T18:47:10","67","2,0,0,0"\n'
'"1041796","21017_0_0","Block H40-H42","1","","","","26/10/2009","2010-02-27T08:57:11","2014-11-23T14:54:32","62","0,0,0,0"\n'
'"1033149","21017_0_0","Block H40-H42","","3","2","4","23/03/2010","2010-03-23T12:17:51","","68","0,0,0,1"\n'
'"1037058","21017_0_0","Z138","1","3","5","6","28/06/2010","2009-10-26T16:47:07","","51","2,0,0,0"\n'
'"1024938","","H048","1","1","","","27/02/2010","","2015-02-23T15:33:53","55","0,0,0,0"\n'
'"1016017","","E148","1","","4","6","24/04/2010","2010-06-28T12:31:51","","51","0,0,0,1"\n'
'"1033388","21017_0_0","D226","","3","4","6","25/10/2008","2010-06-08T12:05:46","","68","1,0,0,0"\n'
'"1031625","","H269","","3","6","","8/12/2008","","2015-02-20T16:39:27","55","2,0,0,0"\n'
'"1038882","21017_0_0","D414","1","1","2","","7/08/2008","2010-04-24T13:21:17","","63","0,0,0,0"\n'
'"1030520","","H402","1","","4","","18/05/2007","","","69","0,0,0,1"\n'
'"1003670","","H264","1","3","4","","8/06/2010","","2014-11-24T10:45:15","55","1,0,0,0"\n'
'"1027017","21017_0_0","R103","1","","5","","27/02/2010","","2015-02-23T15:33:53","55","0,0,0,0"\n'
'"1031595","","A498","","","","6","24/04/2010","2010-06-28T12:31:51","","51","0,0,0,1"\n'
'"1008947","21017_0_0","H400","","","","","","2010-06-28T12:31:51","","","51"\n'
)
    test_main_dat = re.sub("\t+", ",", test_main_dat)
    #test_main_df = pd.read_csv(StringIO(test_main_dat), delimiter="[ ]+", quotechar="'")
    fn = tmpdir_factory.mktemp("data").join("ukb.csv")
    fn.write(test_main_dat)#test_main_df.to_csv(str(fn), sep=",", quotechar='"', index=False)
    print(fn)
    return str(fn)


@pytest.fixture(scope='module')
def gp_csv(tmpdir_factory):
    test_gp_dat = (   
"eid,	data_provider,	event_dt,	read_2,	read_3,	value1,	value2,	value3\n"
"1037918,	3,	01/01/1980,	,XE0Gu,	\n"
"1037918,	3,	08/05/1984,	,F45..,	\n"
"1037918,	3,	08/12/1986,	229..,	0.0,	\n"
"1016017,	3,	24/12/1964,	XE0of,	\n"
"1041796,	3,	21/09/1966,	4662.,	0.0,	\n"
"1016017,	3,	31/10/1967,	XE0of,	1.0,	2.0,	3.0\n"
        )
    fn = tmpdir_factory.mktemp("data").join("gp.csv")
    #Tabs write out strangely so we swap tabs for commas when outputting
    fn.write(re.sub(',','\t', re.sub("\t+", "",test_gp_dat)))
    print(fn)
    return str(fn)



@pytest.fixture(scope='module')
def showcase_csv(tmpdir_factory):
    test_showcase_dat = (   
"Path,Category,FieldID,Field,Participants,Items,Stability,ValueType,Units,ItemType,Strata,Sexed,Instances,Array,Coding,Notes,Link\n"
"OCT,100016,6070,OCT measured (right),,98849,Complete,Categorical single,,Data,Primary,Unisex,2,1,100274,n1,http://biobank.ctsu.ox.ac.uk/showcase/field.cgi?id=6070\n"
"EYE,100041,6119,Which eye(s) affected by glaucoma,,3970,Complete,Categorical single,,Data,Primary,Unisex,4,1,100515,n2,http://biobank.ctsu.ox.ac.uk/showcase/field.cgi?id=6119\n"
"EYE,100041,6148,Eye problems/disorders,,252799,Complete,Categorical multiple,,Data,Primary,Unisex,4,5,100523,n3,http://biobank.ctsu.ox.ac.uk/showcase/field.cgi?id=6148\n"
"OCT,100016,21017,OCT image slices (left),,87595,Complete,Text,,Bulk,Primary,Unisex,2,2,,n4,http://biobank.ctsu.ox.ac.uk/showcase/field.cgi?id=21017\n"
"SummaryDx,2002,41270,Diagnoses - ICD10,,4131361,Ongoing,Categorical multiple,,Data,Primary,Unisex,1,213,19,n5,http://biobank.ctsu.ox.ac.uk/showcase/field.cgi?id=41270\n"
"Genomics > HLA,100035,22182,HLA imputation values,488265,488265,Accruing,Compound,,Data,Derived,Unisex,1,1,5,n6,http://biobank.ctsu.ox.ac.uk/showcase/field.cgi?id=22182\n"
"R > R,100024,21003,Age when attended assessment centre,502506,573525,Complete,Integer,years,Data,Derived,Unisex,4,1,,Derived,http://biobank.ctsu.ox.ac.uk/showcase/field.cgi?id=21003\n"
"Prospective memory,100031,4286,Time when initial screen shown,211307,239452,Complete,Time,,Data,Primary,Unisex,4,1,,,http://biobank.ctsu.ox.ac.uk/showcase/field.cgi?id=4286\n"
"Symbol digit substitution,122,20137,When symbol digit substitution test completed,120183,120183,Complete,Time,,Data,Primary,Unisex,1,1,,Time sybol complete,http://biobank.ctsu.ox.ac.uk/showcase/field.cgi?id=20137\n"
"Reception,100024,53,Date of attending assessment centre,502506,573525,Complete,Date,,Data,Primary,Unisex,4,1,,Date attend assessment,http://biobank.ctsu.ox.ac.uk/showcase/field.cgi?id=53\n"
        )
    fn = tmpdir_factory.mktemp("data").join("showcase.csv")
    fn.write(test_showcase_dat)
    print(fn)
    return str(fn)






#@pytest.fixture
#def cursor(cnxn):
#    cursor = cnxn.cursor()
#    yield cursor
#    cnxn.rollback()
#
#@pytest.fixture
#def birch_bookshelf_project(cursor):
#    stmt = textwrap.dedent('''
#    INSERT INTO projects(name, description)
#    VALUES ('bookshelf', 'Building a bookshelf from birch plywood')
#    ''')
#    cursor.execute(stmt)
#    stmt = 'SELECT @@IDENTITY'
#    project_id = cursor.execute(stmt).fetchval()
#    stmt = textwrap.dedent('''
#    INSERT INTO project_supplies(project_id, name, quantity, unit_cost)
#    VALUES ({project_id}, 'Birch Plywood', 3, 48.50),
#           ({project_id}, 'Wood Glue', 1, 5.99),
#           ({project_id}, 'Screws', 2, 8.97),
#           ({project_id}, 'Stain', 1, 30.99)
#    ''')
#    cursor.execute(stmt.format(project_id = project_id))
#    yield project_id
#
#@pytest.fixture
#def raised_garden_bed_project(cursor):
#    stmt = textwrap.dedent('''
#    INSERT INTO projects(name, description)
#    VALUES ('bookshelf', 'Assemble a raised garden bed')
#    ''')
#    cursor.execute(stmt)
#    stmt = 'SELECT @@IDENTITY'
#    project_id = cursor.execute(stmt).fetchval()
#    stmt = textwrap.dedent('''
#    INSERT INTO project_supplies(project_id, name, quantity, unit_cost)
#    VALUES ({project_id}, '4x4', 3, 3.75),
#           ({project_id}, '2x8', 8, 4.50),
#           ({project_id}, '2x4', 8, 2.50),
#           ({project_id}, 'Screws', 2, 8.97)
#    ''')
#    cursor.execute(stmt.format(project_id = project_id))
#    yield project_id

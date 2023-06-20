# /home/jlaser/.conda/envs/lynker-dev1/bin/python
""""
Motivation: project needs accurate reporting of test coverage.


Solution: Build all encomapasing test based on the cmake/project build options selected. In the future, this
script can be expanded to be suited for only the models that are requested in a specific run of project.


Rough workflow:
1) Import configs (test_coverage and leave_out)
2) Find all test, source, and header files in repo
3) Prune based on leave_out config
4) Generate text file that ./test/CMakeLists. will read in a create the all encompassing test binary


Author:   Jordan Laser   jlaser@lynker.com


"""
# Imports
from file_tools import *
import os
import sys
import json


# Initialize class and set deault folder ignore
ProjectTest = Files(['test'],['cpp'])
ProjectTest.default_folders_leave_out('test',['googletest','CMakeFile','data','lcoverage'])

# For true runs
config_path     = os.path.abspath(sys.argv[1])
project_path    = os.path.abspath(sys.argv[2])

# Set path
ProjectTest.set_project_path(project_path)

# Read in configs
f_config = open(config_path)
config   = json.load(f_config)

# Set optionos
verbose          = config['verbose'] == 'true'
ProjectTest.verbose = config['verbose'] == 'true'
cmake_options    = config['options']
test_name        = config['test_name']


# Append folders we don't want to search through
ProjectTest.folders_leave_out('test',config['gtest_dirs_leave_out'])


file_str = 'PROJECT TEST COVERAGE REPORT'
file_str += '\n--------------------------\n\n'
file_str += f'test name: {test_name}\n\n'


file_str += '------Build options-----'
for joption in cmake_options:
    val = cmake_options[joption]
    file_str += f'\n{joption} : {val}'

src_leave_out = []
ProjectSrc = Files(['src'],['cpp'])
ProjectSrc.set_project_path(project_path)
ProjectSrc.folders_leave_out('src',config['src_dirs_leave_out'])
ProjectSrc.files_leave_out('src',config['src_leave_out'])
ProjectSrc.find_folders()
ProjectSrc.files = ProjectSrc.find_files()

# Create list of keywords to leave out based on options
test_leave_out = config['gtest_leave_out'].copy()
if cmake_options['DBMI_C_LIB_ACTIVE'] == 'FALSE':
    test_leave_out.append('realizations/catchments/Bmi_C_Adapter_Test.cpp')
    test_leave_out.append('realizations/catchments/Bmi_C_Formulation_Test.cpp')
if cmake_options['DLSTM_TORCH_LIB_ACTIVE'] == 'FALSE':
    test_leave_out.append('models/lstm/include/LSTM_Test.cpp')
    test_leave_out.append('realizations/catchments/LSTM_Realization_Test.cpp')    
if cmake_options['DBMI_FORTRAN_ACTIVE'] == 'FALSE':
    test_leave_out.append('realizations/catchments/Bmi_Fortran_Formulation_Test.cpp')
    test_leave_out.append('realizations/catchments/Bmi_Fortran_Adapter_Test.cpp')    
if cmake_options['DNGEN_ACTIVATE_PYTHON'] == 'FALSE':
    test_leave_out.append('realizations/catchments/Bmi_Py_Adapter_Test.cpp')
    test_leave_out.append('realizations/catchments/Bmi_Py_Formulation_Test.cpp')      
if cmake_options['DNGEN_ACTIVATE_ROUTING'] == 'FALSE':
    test_leave_out.append('routing/Routing_Py_Bind_Test.cpp')
if cmake_options['DMPI_ACTIVE'] == 'FALSE':
    test_leave_out.append('core/nexus/NexusRemoteTests.cpp')


ProjectTest.files_leave_out('test',test_leave_out)
ProjectTest.find_folders()
ProjectTest.files = ProjectTest.find_files()

# Write summary text file
file_str += f'\n\n------Including source files from folders -------\n'        
for jdir in ProjectSrc.folders['src']:
    rel = os.path.relpath(jdir,ProjectSrc.path_to_project)
    file_str += f'{rel}\n'

file_str += f'\n------Excluding source file folders -------\n'        
for jdir in ProjectSrc.folders_ignore_with_file_type['src']:
    rel = os.path.relpath(jdir,ProjectSrc.path_to_project)
    file_str += f'{rel}\n'

file_str += '\n------- source files included -------'
for jfile in ProjectSrc.files['src']:
    file_str += f'\n{jfile}'

file_str += '\n\n------- source files excluded -------'
for jfile in ProjectSrc.files_ignored['src']:
    file_str += f'\n{jfile}'



file_str += f'\n\n------Including googletest files from folders -------\n'        
for jdir in ProjectTest.folders['test']:
    rel = os.path.relpath(jdir,ProjectTest.path_to_project)
    file_str += f'{rel}\n'

file_str += f'\n------Excluding googletest file folders -------\n'        
for jdir in ProjectTest.folders_ignore_with_file_type['test']:
    rel = os.path.relpath(jdir,ProjectTest.path_to_project)
    file_str += f'{rel}\n'      

file_str += '\n------- test files included -------'
for jfile in ProjectTest.files['test']:
    file_str += f'\n{jfile}'

file_str += '\n\n------- test files excluded -------'
for jfile in ProjectTest.files_ignored['test']:
    file_str += f'\n{jfile}'

coverage_path = os.path.join(ProjectTest.path_to_project,'test/coverage/')
text_file = open(coverage_path + f'{test_name}_file_summary.txt','w')
text_file.write(file_str)
text_file.close()

# Write CMakeLists.txt custom test inputs
out_path = os.path.join(coverage_path,f'{test_name}-text.txt')
print(f'Writing to {out_path}')
ntests = len(ProjectTest.files['test'])
nsrcs  = len(ProjectSrc.files['src'])
with open(out_path,'w') as f:
    f.write(config['test_name'])
    f.write('\n')
    f.write(str(ntests + nsrcs))
    f.write('\n')
    for jtest in ProjectSrc.files['src']:
        f.write("../src/" + jtest)
        f.write('\n')
    for jtest in ProjectTest.files['test']:
        f.write(jtest)
        f.write('\n')
    for jlib_extra in config['libs_add']:
        f.write(jlib_extra)
        f.write('\n')        

# # Write CMakeLists.txt custom test inputs for dynamic library
# out_path = os.path.join(coverage_path,f'{test_name}-lib-text.txt')
# print(f'Writing to {out_path}')
# with open(out_path,'w') as f:
#     f.write('everything')
#     f.write('\n')
#     f.write('PUBLIC')
#     f.write('\n')
#     for jtop in ProjectLibsDirs.top_folder:
#         for jfolder in ProjectLibsDirs.folders[jtop]:
#             f.write(jfolder)
#             f.write('\n')            
#     for jfolder in ProjectLibsDirs.folders['extra']:
#         f.write(os.path.join(ProjectLibsDirs.path_to_project,jfolder))
#         f.write('\n')  

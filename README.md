This tool set is designed to produce automated test coverage based on the cmake options for a given project. The aim is for this tool to generate a test coverage report using all googletests that should be executed given the cmake options for a partiular build.

his tool was designed for the Next Generation Water Model, but should generalize to any C++ project that is being tested with googletest. ** Note, the formatting of the generated text file may need to be adjusted to suit how CMakeLists. creates the tests.

# Workflow explanation
A shell script, test_coverage.sh manages the main workflow. The steps are:
1) Search project directory for all test files
2) Cull list of test files based on cmake options
3) Create a text file that cmake will read in that is formatted for input into add_custom_test() ('test_name'-text.txt)
4) Create a text file that summarizes the test files (which were used and which were not) ('test_name'_file_summary.txt)
5) Generate the cmake build system
6) Execute test, collect coverage data, and generate a html of the coverage report.

# Intructions

## configs

In test_coverage.json, include the cmake options under the field "options". Also give this test a name and select verbose bool.

In test_libs.json, the user can provide lists of google tests and folders to exclude. Also, the user must add the project libraries that are being tested. 

## Run it

command 'arg1' 'arg2' 'arg3'
bash test_coverage.sh 'path to test_coverage.json' 'path to test_libs.json' 'path to project'

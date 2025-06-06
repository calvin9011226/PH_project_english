# CMake generated Testfile for 
# Source directory: C:/Users/User/Desktop/研究所/計畫/澎湖/澎湖專案/PH_project_v1/spatialindex-src-2.1.0/test/gtest
# Build directory: C:/Users/User/Desktop/研究所/計畫/澎湖/澎湖專案/PH_project_v1/spatialindex-src-2.1.0/build/test/gtest
# 
# This file includes the relevant testing commands required for 
# testing this directory and lists subdirectories to be tested as well.
if(CTEST_CONFIGURATION_TYPE MATCHES "^([Dd][Ee][Bb][Uu][Gg])$")
  add_test(libsidxtest "C:/Users/User/Desktop/研究所/計畫/澎湖/澎湖專案/PH_project_v1/spatialindex-src-2.1.0/build/bin/libsidxtest")
  set_tests_properties(libsidxtest PROPERTIES  WORKING_DIRECTORY "C:/Users/User/Desktop/研究所/計畫/澎湖/澎湖專案/PH_project_v1/spatialindex-src-2.1.0/build/bin" _BACKTRACE_TRIPLES "C:/Users/User/Desktop/研究所/計畫/澎湖/澎湖專案/PH_project_v1/spatialindex-src-2.1.0/test/gtest/CMakeLists.txt;15;add_test;C:/Users/User/Desktop/研究所/計畫/澎湖/澎湖專案/PH_project_v1/spatialindex-src-2.1.0/test/gtest/CMakeLists.txt;0;")
elseif(CTEST_CONFIGURATION_TYPE MATCHES "^([Rr][Ee][Ll][Ee][Aa][Ss][Ee])$")
  add_test(libsidxtest "C:/Users/User/Desktop/研究所/計畫/澎湖/澎湖專案/PH_project_v1/spatialindex-src-2.1.0/build/bin/libsidxtest")
  set_tests_properties(libsidxtest PROPERTIES  WORKING_DIRECTORY "C:/Users/User/Desktop/研究所/計畫/澎湖/澎湖專案/PH_project_v1/spatialindex-src-2.1.0/build/bin" _BACKTRACE_TRIPLES "C:/Users/User/Desktop/研究所/計畫/澎湖/澎湖專案/PH_project_v1/spatialindex-src-2.1.0/test/gtest/CMakeLists.txt;15;add_test;C:/Users/User/Desktop/研究所/計畫/澎湖/澎湖專案/PH_project_v1/spatialindex-src-2.1.0/test/gtest/CMakeLists.txt;0;")
elseif(CTEST_CONFIGURATION_TYPE MATCHES "^([Mm][Ii][Nn][Ss][Ii][Zz][Ee][Rr][Ee][Ll])$")
  add_test(libsidxtest "C:/Users/User/Desktop/研究所/計畫/澎湖/澎湖專案/PH_project_v1/spatialindex-src-2.1.0/build/bin/libsidxtest")
  set_tests_properties(libsidxtest PROPERTIES  WORKING_DIRECTORY "C:/Users/User/Desktop/研究所/計畫/澎湖/澎湖專案/PH_project_v1/spatialindex-src-2.1.0/build/bin" _BACKTRACE_TRIPLES "C:/Users/User/Desktop/研究所/計畫/澎湖/澎湖專案/PH_project_v1/spatialindex-src-2.1.0/test/gtest/CMakeLists.txt;15;add_test;C:/Users/User/Desktop/研究所/計畫/澎湖/澎湖專案/PH_project_v1/spatialindex-src-2.1.0/test/gtest/CMakeLists.txt;0;")
elseif(CTEST_CONFIGURATION_TYPE MATCHES "^([Rr][Ee][Ll][Ww][Ii][Tt][Hh][Dd][Ee][Bb][Ii][Nn][Ff][Oo])$")
  add_test(libsidxtest "C:/Users/User/Desktop/研究所/計畫/澎湖/澎湖專案/PH_project_v1/spatialindex-src-2.1.0/build/bin/libsidxtest")
  set_tests_properties(libsidxtest PROPERTIES  WORKING_DIRECTORY "C:/Users/User/Desktop/研究所/計畫/澎湖/澎湖專案/PH_project_v1/spatialindex-src-2.1.0/build/bin" _BACKTRACE_TRIPLES "C:/Users/User/Desktop/研究所/計畫/澎湖/澎湖專案/PH_project_v1/spatialindex-src-2.1.0/test/gtest/CMakeLists.txt;15;add_test;C:/Users/User/Desktop/研究所/計畫/澎湖/澎湖專案/PH_project_v1/spatialindex-src-2.1.0/test/gtest/CMakeLists.txt;0;")
else()
  add_test(libsidxtest NOT_AVAILABLE)
endif()
subdirs("gtest-1.14.0")
